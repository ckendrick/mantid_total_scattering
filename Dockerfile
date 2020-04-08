# Install mantid image
FROM mantidproject/mantid:nightly

# Add Mantid to python path
ENV MANTIDPATH         /opt/mantidnightly/bin
ENV TSREPO             /root/mantid_total_scattering
ENV PYTHONPATH         ${MANTIDPATH}:${TSREPO}:${PYTHONPATH}

# Install python dependencies
RUN yum update -y && \
    yum install python3-pip curl git -y && \
    pip3 install pytest codecov && \
    yum clean all

# Copy git content from current branch
COPY . /root/mantid_total_scattering

# Move to work directory
WORKDIR $TSREPO
