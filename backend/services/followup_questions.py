from __future__ import annotations

from schemas.request_response import (
    FollowUpInputType,
    FollowUpQuestionField,
    FollowUpQuestionPack,
    InternalRoute,
)

PACKS_BY_ROUTE: dict[InternalRoute, FollowUpQuestionPack] = {
    InternalRoute.china: FollowUpQuestionPack(
        pack_id="adaptive_pack_alpha",
        title="Additional project details",
        description="Provide a few project volume details to refine the estimate.",
        fields=[
            FollowUpQuestionField(
                field_key="transaction_volume",
                label="Estimated monthly transaction volume",
                input_type=FollowUpInputType.integer,
                required=True,
                min_value=1,
                max_value=1_000_000,
                placeholder="e.g. 25000",
            ),
            FollowUpQuestionField(
                field_key="change_request_volume",
                label="Expected annual change requests",
                input_type=FollowUpInputType.integer,
                required=True,
                min_value=0,
                max_value=20_000,
                placeholder="e.g. 120",
            ),
            FollowUpQuestionField(
                field_key="integration_points",
                label="Approximate number of external integrations",
                input_type=FollowUpInputType.integer,
                required=True,
                min_value=0,
                max_value=1_000,
                placeholder="e.g. 12",
            ),
            FollowUpQuestionField(
                field_key="expected_reuse_percent",
                label="Estimated percentage of reusable components",
                input_type=FollowUpInputType.number,
                required=False,
                min_value=0,
                max_value=100,
                step=1,
                placeholder="e.g. 35",
            ),
        ],
    ),
    InternalRoute.cocomo81: FollowUpQuestionPack(
        pack_id="adaptive_pack_beta",
        title="Additional project details",
        description="Provide implementation and constraints details to refine the estimate.",
        fields=[
            FollowUpQuestionField(
                field_key="estimated_kloc",
                label="Estimated code size (KLOC)",
                input_type=FollowUpInputType.number,
                required=True,
                min_value=0.1,
                max_value=1000,
                step=0.1,
                placeholder="e.g. 45.5",
            ),
            FollowUpQuestionField(
                field_key="platform_constraint_level",
                label="Platform constraint level",
                input_type=FollowUpInputType.select,
                required=True,
                options=["relaxed", "nominal", "tight"],
            ),
            FollowUpQuestionField(
                field_key="tooling_maturity",
                label="Tooling and automation maturity",
                input_type=FollowUpInputType.select,
                required=True,
                options=["low", "medium", "high"],
            ),
            FollowUpQuestionField(
                field_key="schedule_compression",
                label="Schedule compression pressure",
                input_type=FollowUpInputType.select,
                required=False,
                options=["low", "medium", "high"],
            ),
        ],
    ),
    InternalRoute.desharnais: FollowUpQuestionPack(
        pack_id="adaptive_pack_gamma",
        title="Additional project details",
        description="Provide process and data scope details to refine the estimate.",
        fields=[
            FollowUpQuestionField(
                field_key="business_process_count",
                label="Number of core business processes",
                input_type=FollowUpInputType.integer,
                required=True,
                min_value=1,
                max_value=2000,
                placeholder="e.g. 35",
            ),
            FollowUpQuestionField(
                field_key="expected_change_requests",
                label="Expected change requests during delivery",
                input_type=FollowUpInputType.integer,
                required=True,
                min_value=0,
                max_value=20_000,
                placeholder="e.g. 80",
            ),
            FollowUpQuestionField(
                field_key="data_complexity_index",
                label="Data complexity index (1-10)",
                input_type=FollowUpInputType.number,
                required=True,
                min_value=1,
                max_value=10,
                step=0.1,
                placeholder="e.g. 6.5",
            ),
            FollowUpQuestionField(
                field_key="team_distribution",
                label="Team distribution",
                input_type=FollowUpInputType.select,
                required=False,
                options=["co_located", "hybrid", "distributed"],
            ),
        ],
    ),
}

PACKS_BY_ID: dict[str, FollowUpQuestionPack] = {pack.pack_id: pack for pack in PACKS_BY_ROUTE.values()}
ROUTE_BY_PACK_ID: dict[str, InternalRoute] = {pack.pack_id: route for route, pack in PACKS_BY_ROUTE.items()}


def get_followup_pack_for_route(route: InternalRoute) -> FollowUpQuestionPack:
    return PACKS_BY_ROUTE[route]


def get_followup_pack_by_id(pack_id: str) -> FollowUpQuestionPack:
    pack = PACKS_BY_ID.get(pack_id)
    if pack is None:
        raise ValueError(f"Unknown follow-up pack id: {pack_id}")
    return pack


def normalize_followup_answers(pack: FollowUpQuestionPack, answers: dict[str, object]) -> tuple[dict[str, object], list[str]]:
    normalized: dict[str, object] = {}
    unresolved_fields: list[str] = []

    for field in pack.fields:
        raw = answers.get(field.field_key)

        if raw is None:
            if field.required:
                raise ValueError(f"Missing required follow-up field: {field.field_key}")
            unresolved_fields.append(field.field_key)
            continue

        if field.input_type == FollowUpInputType.integer:
            value = int(raw)
            if field.min_value is not None and value < field.min_value:
                raise ValueError(f"{field.field_key} must be >= {field.min_value}")
            if field.max_value is not None and value > field.max_value:
                raise ValueError(f"{field.field_key} must be <= {field.max_value}")
            normalized[field.field_key] = value
            continue

        if field.input_type == FollowUpInputType.number:
            value = float(raw)
            if field.min_value is not None and value < field.min_value:
                raise ValueError(f"{field.field_key} must be >= {field.min_value}")
            if field.max_value is not None and value > field.max_value:
                raise ValueError(f"{field.field_key} must be <= {field.max_value}")
            normalized[field.field_key] = round(value, 4)
            continue

        if field.input_type == FollowUpInputType.select:
            value = str(raw).strip().lower()
            options = field.options or []
            if value not in options:
                raise ValueError(f"{field.field_key} must be one of: {', '.join(options)}")
            normalized[field.field_key] = value
            continue

        if field.input_type == FollowUpInputType.boolean:
            if isinstance(raw, bool):
                normalized[field.field_key] = raw
            elif str(raw).strip().lower() in {"true", "1", "yes"}:
                normalized[field.field_key] = True
            elif str(raw).strip().lower() in {"false", "0", "no"}:
                normalized[field.field_key] = False
            else:
                raise ValueError(f"{field.field_key} must be boolean")
            continue

        # Text type — sanitize and validate length.
        import re
        value = str(raw).strip()
        # Strip HTML/script tags
        value = re.sub(r"<[^>]+>", "", value)
        if len(value) > 2000:
            value = value[:2000]
        if field.required and not value:
            raise ValueError(f"{field.field_key} cannot be empty")
        normalized[field.field_key] = value

    return normalized, unresolved_fields

