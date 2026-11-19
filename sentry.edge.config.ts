import * as Sentry from "@sentry/nextjs";

const dsn = process.env.SENTRY_DSN;

if (dsn) {
  Sentry.init({
    dsn,
    tracesSampleRate: process.env.NODE_ENV === "production" ? 0.1 : 1.0,
    // This config is not imported by anything: `instrumentation.ts` registers only the `nodejs`
    // branch and no route declares `runtime = "edge"`. The strip is here so that adding that branch
    // does not simultaneously add an edge surface that reports a request body.
    beforeSend(event) {
      if (event.request?.data) {
        delete event.request.data;
      }
      return event;
    },
  });
}
