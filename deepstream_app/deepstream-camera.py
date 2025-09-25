#!/usr/bin/env python3

import sys
# This path is set by the PYTHONPATH environment variable in docker-compose
# sys.path.append('/opt/nvidia/deepstream/deepstream-7.1/sources/deepstream_python_apps/')
import gi
gi.require_version('Gst', '1.0')
# Import the RTSP Server library
gi.require_version('GstRtspServer', '1.0')
from gi.repository import GLib, Gst, GstRtspServer
from common.bus_call import bus_call
from datetime import datetime
import pyds

PGIE_CLASS_ID_VEHICLE = 0
PGIE_CLASS_ID_BICYCLE = 1
PGIE_CLASS_ID_PERSON = 2
PGIE_CLASS_ID_ROADSIGN = 3
LOG_FILE_PATH = "/log/log.txt"

def osd_sink_pad_buffer_probe(pad, info, u_data):
    # This function's role is to log metadata, which it does perfectly.
    frame_number=0
    gst_buffer = info.get_buffer()
    if not gst_buffer: return
    batch_meta = pyds.gst_buffer_get_nvds_batch_meta(hash(gst_buffer))
    l_frame = batch_meta.frame_meta_list
    while l_frame is not None:
        try:
            frame_meta = pyds.NvDsFrameMeta.cast(l_frame.data)
        except StopIteration: break
        frame_number=frame_meta.frame_num
        l_obj=frame_meta.obj_meta_list
        with open(LOG_FILE_PATH, "a") as log_file:
            while l_obj is not None:
                try:
                    obj_meta=pyds.NvDsObjectMeta.cast(l_obj.data)
                except StopIteration: break
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
                log_entry = (f"{timestamp}, Frame:{frame_number}, ClassID:{obj_meta.class_id}, "
                             f"Confidence:{obj_meta.confidence:.4f}\n")
                print(log_entry, flush=True)
                log_file.write(log_entry)
                try: l_obj=l_obj.next
                except StopIteration: break
        try: l_frame=l_frame.next
        except StopIteration: break
    return Gst.PadProbeReturn.OK

def main(args):
    if len(args) != 2:
        sys.stderr.write("usage: %s <v4l2-device-path>\n" % args[0])
        sys.exit(1)

    Gst.init(None)
    pipeline = Gst.Pipeline()
    if not pipeline: sys.stderr.write(" Unable to create Pipeline \n")

    # --- Create GStreamer Elements ---
    source = Gst.ElementFactory.make("v4l2src", "usb-cam-source")
    caps_v4l2src = Gst.ElementFactory.make("capsfilter", "v4l2src_caps")
    videoconvert = Gst.ElementFactory.make("videoconvert", "convertor_src1")
    nvvidconvsrc = Gst.ElementFactory.make("nvvideoconvert", "convertor_src2")
    caps_vidconvsrc = Gst.ElementFactory.make("capsfilter", "nvmm_caps")
    streammux = Gst.ElementFactory.make("nvstreammux", "Stream-muxer")
    pgie = Gst.ElementFactory.make("nvinfer", "primary-inference")
    nvvidconv = Gst.ElementFactory.make("nvvideoconvert", "convertor")
    nvosd = Gst.ElementFactory.make("nvdsosd", "onscreendisplay")
    
    # --- Elements for creating the RTSP stream ---
    transform = Gst.ElementFactory.make("nvvideoconvert", "transform")
    encoder = Gst.ElementFactory.make("nvv4l2h264enc", "encoder")
    rtppay = Gst.ElementFactory.make("rtph264pay", "rtppay")
    sink = Gst.ElementFactory.make("udpsink", "udpsink")

    # --- Set properties for the elements ---
    source.set_property('device', args[1])
    caps_v4l2src.set_property('caps', Gst.Caps.from_string("video/x-raw, framerate=30/1, width=1280, height=720"))
    caps_vidconvsrc.set_property('caps', Gst.Caps.from_string("video/x-raw(memory:NVMM)"))
    streammux.set_property('width', 1280)
    streammux.set_property('height', 720)
    streammux.set_property('batch-size', 1)
    # This should point to your AI model's config file, e.g., dstest1_pgie_config.txt
    pgie.set_property('config-file-path', "config.txt")
    encoder.set_property('bitrate', 4000000)
    sink.set_property('host', '0.0.0.0')
    sink.set_property('port', 5400)
    sink.set_property('sync', False)

    # --- Add elements to pipeline ---
    for element in [source, caps_v4l2src, videoconvert, nvvidconvsrc, caps_vidconvsrc, streammux, pgie, nvvidconv, nvosd, transform, encoder, rtppay, sink]:
        pipeline.add(element)

    # --- Link elements in the correct order ---
    source.link(caps_v4l2src)
    caps_v4l2src.link(videoconvert)
    videoconvert.link(nvvidconvsrc)
    nvvidconvsrc.link(caps_vidconvsrc)
    sinkpad = streammux.get_request_pad("sink_0")
    srcpad = caps_vidconvsrc.get_static_pad("src")
    srcpad.link(sinkpad)
    streammux.link(pgie)
    pgie.link(nvvidconv)
    nvvidconv.link(nvosd)
    nvosd.link(transform)
    transform.link(encoder)
    encoder.link(rtppay)
    rtppay.link(sink)

    # Add probe for metadata
    osdsinkpad = nvosd.get_static_pad("sink")
    osdsinkpad.add_probe(Gst.PadProbeType.BUFFER, osd_sink_pad_buffer_probe, 0)
    
    # --- Create and start the RTSP server ---
    server = GstRtspServer.RTSPServer.new()
    server.props.service = "8554"
    server.attach(None)
    factory = GstRtspServer.RTSPMediaFactory.new()
    factory.set_launch(f'( udpsrc port=5400 caps = "application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)H264, payload=(int)96" )')
    factory.set_shared(True)
    server.get_mount_points().add_factory("/ds-feed", factory)

    # Start pipeline
    loop = GLib.MainLoop()
    pipeline.set_state(Gst.State.PLAYING)
    print("\n *** RTSP Stream is available at rtsp://localhost:8554/ds-feed *** \n")
    try:
        loop.run()
    except:
        pass
    pipeline.set_state(Gst.State.NULL)

if __name__ == '__main__':
    sys.exit(main(sys.argv))


