FROM debian:jessie

ARG PHANTOM_JS_VERSION
ENV PHANTOM_JS_VERSION ${PHANTOM_JS_VERSION:-2.1.1-linux-x86_64}

ENV PYTHONIOENCODING utf-8
ENV TZ Asia/Seoul

# Install runtime dependencies
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
        ca-certificates \
        cron \
        bzip2 \
        libfontconfig \
        python-pip \
        python-urllib3 \
        python-yaml \
 && pip install --ignore-installed \
        selenium \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# Install official PhantomJS release
RUN set -x  \
 && apt-get update \
 && apt-get install -y --no-install-recommends \
        curl \
 && mkdir /tmp/phantomjs \
 && curl -L https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-${PHANTOM_JS_VERSION}.tar.bz2 \
        | tar -xj --strip-components=1 -C /tmp/phantomjs \
 && mv /tmp/phantomjs/bin/phantomjs /usr/local/bin \
 && apt-get purge --auto-remove -y \
        curl \
 && apt-get clean \
 && rm -rf /tmp/* /var/lib/apt/lists/*

# add and set permission of scripts
COPY /root /
RUN chmod +x /usr/bin/makerss*

VOLUME /config /rssxml
EXPOSE 8910
CMD ["makerss_init"]
