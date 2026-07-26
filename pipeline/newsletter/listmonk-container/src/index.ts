import { Container, getContainer } from "@cloudflare/containers";

interface Env {
  LISTMONK_CONTAINER: DurableObjectNamespace<ListmonkContainer>;
  PGHOST: string;
  PGPORT: string;
  PGUSER: string;
  PGPASSWORD: string;
  PGDATABASE: string;
  PGSSLMODE: string;
  LISTMONK_ADMIN_USER: string;
  LISTMONK_ADMIN_PASSWORD: string;
}

export class ListmonkContainer extends Container<Env> {
  defaultPort = 9000;
  // Postgres lives on Neon, not in this container — sleeping loses zero
  // data, just adds ~1-3s cold start on the next request (e.g. someone
  // clicking a confirm/unsubscribe link in an old email).
  sleepAfter = "10m";
  envVars: Record<string, string> = {};

  constructor(...args: ConstructorParameters<typeof Container<Env>>) {
    const [ctx, env] = args;
    super(ctx, env);
    this.envVars = {
      LISTMONK_app__address: "0.0.0.0:9000",
      LISTMONK_db__host: env.PGHOST,
      LISTMONK_db__port: env.PGPORT,
      LISTMONK_db__user: env.PGUSER,
      LISTMONK_db__password: env.PGPASSWORD,
      LISTMONK_db__database: env.PGDATABASE,
      LISTMONK_db__ssl_mode: env.PGSSLMODE,
      // Small pool — Neon free tier has limited concurrent connections,
      // and this is a personal blog, not a high-traffic app. listmonk's
      // docker-compose.yml default (25/25) is way oversized for this.
      LISTMONK_db__max_open: "4",
      LISTMONK_db__max_idle: "2",
      LISTMONK_db__max_lifetime: "300s",
      LISTMONK_ADMIN_USER: env.LISTMONK_ADMIN_USER,
      LISTMONK_ADMIN_PASSWORD: env.LISTMONK_ADMIN_PASSWORD,
    };
  }

  override onStart() {
    console.log("listmonk container started");
  }
  override onError(error: unknown) {
    console.log("listmonk container error:", error);
  }
}

export default {
  async fetch(request: Request, env: Env) {
    // Fixed singleton — one listmonk instance for the whole blog, not
    // per-request/per-user routing.
    const container = getContainer(env.LISTMONK_CONTAINER, "main");
    return container.fetch(request);
  },
};
