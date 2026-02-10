FROM mcr.microsoft.com/devcontainers/python:3.11

RUN mkdir -p /home/vscode/.cache/data_juicer/models \
    && curl -o /home/vscode/.cache/data_juicer/models/en.arpa.bin \
       https://dail-wlcb.oss-cn-wulanchabu.aliyuncs.com/data_juicer/models/en.arpa.bin \
    && curl -o /home/vscode/.cache/data_juicer/models/lid.176.bin \
       https://dail-wlcb.oss-cn-wulanchabu.aliyuncs.com/data_juicer/models/lid.176.bin \
    && chown -R vscode:vscode /home/vscode/.cache
