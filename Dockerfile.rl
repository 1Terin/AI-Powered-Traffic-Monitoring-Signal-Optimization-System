FROM python:3.11-slim
WORKDIR /usr/src/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN python -m pip install --upgrade pip \
    && python -m pip install --no-cache-dir gymnasium numpy paho-mqtt stable-baselines3 torch --extra-index-url https://download.pytorch.org/whl/cpu
COPY ml/train_rl.py ./ml/train_rl.py
COPY ml/rl_signal_opt.py ./ml/rl_signal_opt.py
ENV MQTT_BROKER=mqtt://mqtt:1883
CMD ["python", "./ml/train_rl.py", "--timesteps", "2000", "--live-steps", "30", "--interval", "5"]
