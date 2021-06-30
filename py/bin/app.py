from flask import Flask, render_template, request
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

trace.set_tracer_provider(
    TracerProvider(
        resource=Resource.create({SERVICE_NAME: "py-service"})
    )
)

jaeger_exporter = JaegerExporter(agent_host_name="jaeger", agent_port=6831,)

trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)

tracer = trace.get_tracer(__name__)

def sendTrace():
    with tracer.start_as_current_span("foo"):
        with tracer.start_as_current_span("bar"):
            with tracer.start_as_current_span("baz"):
                print("Hello Splunk")
                return "Trace complete"

# Create Flask's `app` object
app = Flask(
    __name__,
    instance_relative_config=False,
    template_folder="templates"
)

@app.route('/', methods=['GET'])
def getIndex():
    trace = sendTrace()
    return render_template("index.html", msg=trace)

@app.route('/', methods=['POST'])
def postIndex():
    return sendTrace()

if __name__ == "__main__":
    app.run(host ='0.0.0.0', port = 5000, debug = True)
