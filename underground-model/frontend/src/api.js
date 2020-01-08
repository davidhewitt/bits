/**
 * Simple implementation to query the heroku API for stats.
 */

// NB: This frontend expects the backend to be running (bin/serve.py)
const API = "http://localhost:5000";

const ROUTE_REGEX = /How do I get from (.*?) to (.*?)\?/;
const INTERCHANGES_REGEX = /What lines does (.*?) serve\?/;

export async function queryApi(query) {
  const route = query.match(ROUTE_REGEX);
  if (route) {
    const [, start, destination] = route;
    const response = await fetch(`${API}/route/${start}/${destination}`);
    const journey = await response.json();

    if (journey.error) {
      return [journey.error, true];
    }

    const segments = journey.map(seg => `the ${seg.line} to ${seg.destination}`);
    const directions = `Take ${segments.join(", then take ")}.`;

    return [directions, true];
  }

  const interchanges = query.match(INTERCHANGES_REGEX);
  if (interchanges) {
    const [, station] = interchanges;

    const response = await fetch(`${API}/station/${station}/interchanges`);
    const lines = await response.json();

    if (lines.error) {
      return [lines.error, true];
    }

    if (lines.length == 1) {
      return [`Just ${lines[0]}.`, true];
    } else {
      const result =
      `${lines.slice(0, -1).join(", ")} and ${lines[lines.length - 1]}.`;

      return [result, true];
    }
  }

  return ["error", false];
}
