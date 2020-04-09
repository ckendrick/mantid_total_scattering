# Install mantid image
FROM mantidproject/mantid:nightly

# Add Mantid to python path
ENV MANTIDPATH         /opt/mantidnightly/bin
ENV TSREPO             /root/mantid_total_scattering
ENV PYTHONPATH         ${MANTIDPATH}:${TSREPO}:${PYTHONPATH}

# Install python dependencies
RUN yum update -y && \
    yum install python3-pip curl git -y && \
    pip3 install pytest codecov flake8 && \
    yum clean all

# Copy Insturment geometry caches
RUN mkdir -p /root/.mantid/instrument/geometryCache
COPY ./tests/data/POLARIS9fbf7121b4274c833043ae8933ec643ff7b9313d.vtp /root/.mantid/instrument/geometryCache/POLARIS9fbf7121b4274c833043ae8933ec643ff7b9313d.vtp

# Hack for seg fault when DownloadInstrument gets called inside container from "import mantid.simpleapi"
RUN echo "UpdateInstrumentDefinitions.OnStartup = 0" > /root/.mantid/Mantid.user.properties

# Copy git content from current branch
COPY . /root/mantid_total_scattering

# Move to work directory
WORKDIR $TSREPO
