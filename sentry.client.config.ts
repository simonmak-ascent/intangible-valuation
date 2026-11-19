import * as Sentry from "@sentry/nextjs";

const dsn = process.env.NEXT_PUBLIC_SENTRY_DSN;

if (dsn) {
  Sentry.init({
    dsn,
    tracesSampleRate: process.env.NODE_ENV === "production" ? 0.1 : 1.0,
    // No Session Replay. This file would have enabled it at 0.1 session / 1.0 error, resting only on
    // the library's default masking, on a site whose every page is a form taking financial figures —
    // and this deployment has no account to consent on its behalf. The options are removed rather
    // than left for the day a `withSentryConfig` wrapper loads this file: there is no
    // `instrumentation-client.ts` and no wrapper today, so nothing here is live, which is exactly why
    // it is worth deleting now instead of discovering it later.
    beforeSend(event) {
      // Strip financial data from error reports
      if (event.request?.data) {
        delete event.request.data;
      }
      return event;
    },
  });
}
