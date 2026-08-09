import { Container, getContainer } from "@cloudflare/containers";

interface Env {
  HELLO_CONTAINER: DurableObjectNamespace<HelloContainer>;
}

export class HelloContainer extends Container<Env> {
  defaultPort = 5678;
  sleepAfter = "10m";

  override onStart() {
    console.log("hello container started");
  }
  override onError(error: unknown) {
    console.log("hello container error:", error);
  }
}

export default {
  async fetch(request: Request, env: Env) {
    const container = getContainer(env.HELLO_CONTAINER, "main");
    return container.fetch(request);
  },
};
