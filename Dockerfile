FROM golang:1.26.0 AS builder-amd64
ARG ARCH=amd64

FROM golang:1.26.0 AS builder-arm64
ARG ARCH=arm64

FROM builder-$TARGETARCH AS builder

ARG UPSTREAM_VERSION
ARG UPSTREAM_COMMIT
WORKDIR /tmp/ingress-gce

COPY .ci/checkout-upstream.sh /usr/local/bin/checkout-upstream.sh
RUN sh /usr/local/bin/checkout-upstream.sh "$UPSTREAM_VERSION" "$UPSTREAM_COMMIT" .

RUN GO111MODULE=on CGO_ENABLED=0 GOOS=linux GOARCH="$ARCH" GOPROXY=${GOPROXY} go build \
    -trimpath \
    -ldflags="-X k8s.io/ingress-gce/pkg/version.Version=${UPSTREAM_VERSION} -X k8s.io/ingress-gce/pkg/version.GitCommit=${UPSTREAM_COMMIT}" \
    -o=glbc \
    ./cmd/glbc

### actual container

FROM gcr.io/distroless/static:latest

COPY --from=builder /tmp/ingress-gce/glbc /bin/glbc

ENTRYPOINT ["/bin/glbc"]
