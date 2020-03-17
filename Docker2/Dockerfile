FROM stepone:1.3.2
WORKDIR /usr/local/test/
COPY . .
ARG DEBIAN_FRONTEND=noninteractive
RUN ./pipinstall.sh
ENTRYPOINT ["/usr/local/test/trialrun.sh"]
