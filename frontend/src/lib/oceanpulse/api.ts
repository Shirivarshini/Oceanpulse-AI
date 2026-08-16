import type { Analysis, Scenario } from "./types";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

export async function analyzeScenario(
  scenario: Scenario,
): Promise<Analysis> {
  const response = await fetch(`${API_BASE_URL}/api/demo/analyze`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ scenario }),
  });

  if (!response.ok) {
    throw new Error(
      `Backend request failed: ${response.status} ${response.statusText}`,
    );
  }

  return response.json() as Promise<Analysis>;
}