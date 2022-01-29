FROM python:3.9
WORKDIR /monitor
ADD requirements.txt /monitor/requirements.txt
RUN apt update && apt install -y pulseaudio pulseaudio-utils portaudio19-dev
RUN pip install -r requirements.txt
ADD . /monitor
RUN dbus-uuidgen > /var/lib/dbus/machine-id
RUN mkdir -p /var/run/dbus
RUN dbus-daemon --config-file=/usr/share/dbus-1/system.conf --print-address
RUN pulseaudio -D --exit-idle-time=-1
ENTRYPOINT ["python", "-m", "uvicorn", "main:app", "--reload", "--host", "0.0.0.0"]
