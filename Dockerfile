FROM golang:1.22.7 AS builder
ENV CGO_ENABLED=0
COPY . .
WORKDIR ingress-gce
RUN go install -v ./cmd/glbc

# ### actual container
FROM gcr.io/distroless/static:latest
COPY --from=builder /go/bin/glbc /glbc

ENTRYPOINT ["/glbc"]
