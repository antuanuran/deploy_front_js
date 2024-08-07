FROM nvcr.io/nvidia/pytorch:24.05-py3
USER root
ENV DEBIAN_FRONTEND=noninteractive

RUN pip uninstall -y opencv-python
RUN apt-get update
RUN apt-get install -y \
            build-essential \
            pkg-config \
            libgstreamer1.0-0 \
            gstreamer1.0-plugins-base \
            gstreamer1.0-plugins-good \
            gstreamer1.0-plugins-bad \
            gstreamer1.0-plugins-ugly \
            gstreamer1.0-libav \
            gtk-doc-tools \
            libgstreamer1.0-dev \
            libgstreamer-plugins-base1.0-dev \
            cmake \
            protobuf-compiler \
            libgtk2.0-dev \
            ocl-icd-opencl-dev \
            ca-certificates \
            libssl-dev

ARG CACHEBUST=1
WORKDIR /
COPY libnv libnv
COPY /modules/gst-plugins-bad /gst-plugins-bad
WORKDIR /gst-plugins-bad

# Build plugin nvh264dec and nvh264enc
# Run 'git clone https://github.com/GStreamer/gst-plugins-bad.git'
RUN git checkout 1.16.2
RUN cp /libnv/libnvcuvid.so /usr/local/cuda/lib64
RUN cp /libnv/libnvidia-encode.so /usr/local/cuda/lib64
RUN cp /usr/local/cuda/include/cuda.h /gst-plugins-bad/sys/nvenc
RUN NVENCODE_CFLAGS="-I/gst-plugins-bad/sys/nvenc" ./autogen.sh --with-cuda-prefix="/usr/local/cuda" --disable-gtk-doc
WORKDIR /gst-plugins-bad/sys/nvenc
RUN make
RUN cp .libs/libgstnvenc.so /usr/lib/x86_64-linux-gnu/gstreamer-1.0/
WORKDIR /gst-plugins-bad/sys/nvdec
RUN make
RUN cp .libs/libgstnvdec.so /usr/lib/x86_64-linux-gnu/gstreamer-1.0/

RUN apt-get update && apt-get -y --no-install-recommends install \
            gstreamer1.0-tools \
            gstreamer1.0-python3-plugin-loader \
            libgstrtspserver-1.0-dev
RUN pip3 install -U wheel pip setuptools
COPY ./requirements/ /app/requirements/
RUN pip install -r /app/requirements/requirements.txt

# Build plugin rtponvifmetadatapay
# Run 'git clone https://gitlab.freedesktop.org/gstreamer/gst-plugins-rs.git'
WORKDIR /
RUN apt-get install -y cargo
COPY /modules/gst-plugins-rs /gst-plugins-rs
WORKDIR /gst-plugins-rs/net/onvif/
RUN cargo build
RUN mkdir -p ~/.local/share/gstreamer-1.0/plugins/
RUN cp ../../target/debug/libgstrsonvif.so ~/.local/share/gstreamer-1.0/plugins/

RUN apt-get install -y ffmpeg
ADD . /app
RUN mkdir -pv ~/.cache/xdgr
ENV XDG_RUNTIME_DIR=$PATH:~/.cache/xdgr
ENV GST_GL_WINDOW=egl-device
ENV GST_PLUGIN_PATH /usr/lib/gstreamer-1.0/:/app/gstream/src/
ENV GST_DEBUG_DUMP_DOT_DIR=/app/tmp/dot
ENV PYTHONPATH=$PYTHONPATH:/app/gstream/src
CMD ["python3", "-u", "/app/gstream/src/app.py"]