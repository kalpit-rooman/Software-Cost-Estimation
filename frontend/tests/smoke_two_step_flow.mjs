/*
 * Frontend smoke test for the public two-step adaptive flow.
 *
 * Usage:
 *   node tests/smoke_two_step_flow.mjs
 *
 * Optional env override:
 *   set NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
 */

const API_BASE = (process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000").replace(/\/$/, "");

function buildFollowUpAnswers(pack) {
  const packDefaults = {
    adaptive_pack_alpha: {
      transaction_volume: 1000,
      change_request_volume: 20,
      integration_points: 3,
      expected_reuse_percent: 50,
    },
    adaptive_pack_beta: {
      estimated_kloc: 12,
      platform_constraint_level: "nominal",
      tooling_maturity: "medium",
      schedule_compression: "low",
    },
    adaptive_pack_gamma: {
      business_process_count: 8,
      expected_change_requests: 10,
      data_complexity_index: 2.0,
      team_distribution: "hybrid",
    },
  };

  const answers = {};
  for (const field of pack.fields || []) {
    const preset = packDefaults[pack.pack_id]?.[field.field_key];
    if (preset !== undefined) {
      answers[field.field_key] = preset;
      continue;
    }

    if (field.input_type === "select") {
      answers[field.field_key] = field.options?.[0] ?? "";
      continue;
    }
    if (field.input_type === "boolean") {
      answers[field.field_key] = true;
      continue;
    }
    if (field.input_type === "integer") {
      answers[field.field_key] = Math.max(1, Number(field.min_value ?? 1));
      continue;
    }
    if (field.input_type === "number") {
      answers[field.field_key] = Math.max(0.1, Number(field.min_value ?? 1));
      continue;
    }
    answers[field.field_key] = "smoke-test";
  }
  return answers;
}

async function postJson(path, body) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(`POST ${path} failed (${res.status}): ${JSON.stringify(data)}`);
  }
  return data;
}

async function run() {
  console.log(`Running two-step smoke test against ${API_BASE}`);

  const candidateBriefs = [
    {
      num_screens: 12,
      num_entities: 10,
      duration_months: 12,
      team_experience_years: 7,
      pm_experience_years: 8,
      complexity: "high",
      reliability: "high",
      team_size: 10,
      project_notes: "smoke test run profile A",
    },
    {
      num_screens: 8,
      num_entities: 9,
      duration_months: 8,
      team_experience_years: 5,
      pm_experience_years: 6,
      complexity: "low",
      reliability: "medium",
      team_size: 5,
      project_notes: "smoke test run profile B",
    },
    {
      num_screens: 6,
      num_entities: 7,
      duration_months: 6,
      team_experience_years: 3,
      pm_experience_years: 4,
      complexity: "low",
      reliability: "low",
      team_size: 3,
      project_notes: "smoke test run profile C",
    },
  ];

  let final = null;
  let lastError = null;

  for (const brief of candidateBriefs) {
    try {
      const intake = await postJson("/predict/intake", {
        project_brief: brief,
        target_currency: "USD",
        version: 1,
      });

      if (!intake.intake_id || !intake.follow_up_pack) {
        throw new Error("Stage 1 response missing intake_id or follow_up_pack");
      }

      const followUpAnswers = buildFollowUpAnswers(intake.follow_up_pack);

      final = await postJson("/predict/final", {
        intake_id: intake.intake_id,
        follow_up_answers: followUpAnswers,
        target_currency: "USD",
      });
      break;
    } catch (err) {
      lastError = err;
    }
  }

  if (!final) {
    throw lastError || new Error("Unable to complete two-step flow");
  }

  if (!final.estimated_effort || !final.cost_breakdown) {
    throw new Error("Stage 2 response missing estimated_effort or cost_breakdown");
  }

  console.log("Smoke test passed.");
  console.log(`intake_id=${final.intake_id}`);
  console.log(`effort_months=${final.estimated_effort.effort_months}`);
  console.log(`display_cost=${final.cost_breakdown.display_cost} ${final.cost_breakdown.target_currency}`);
  console.log(`mode=${final.estimated_effort.prediction_mode}`);
}

run().catch((err) => {
  console.error("Smoke test failed:", err.message || err);
  process.exit(1);
});
