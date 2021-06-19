from elasticsearch import Elasticsearch

es_client = Elasticsearch("http://elastic:devpass@localhost:9200")

CRON = "0 0/5 * * * ?"  # When should this run?
INTERVAL = "1m"         # Agg over what interval?

# Create ILM for retaining al_metrics*_rollup indices for X period
ILM = {
    "rollup-al_metrics-policy": {
        "policy": {
            "phases": {
                "cold": {
                    "min_age": "0d",
                    "actions": {
                        "set_priority": {
                            "priority": 0
                        }
                    }
                },
                "hot": {
                    "min_age": "0ms",
                    "actions": {
                        "rollover": {
                            "max_age": "1h"
                        },
                        "set_priority": {
                            "priority": 100
                        }
                    }
                }
            }
        }
    }
}

for k, v in ILM.items():
    es_client.ilm.put_lifecycle(policy=k, body=v)

# Create component template setting the lifecycle
COMPONENT = {
    "template": {
        "settings": {
            "index": {
                "lifecycle": {
                    "name": "rollup-al_metrics-policy"
                }
            }
        }
    }
}

es_client.cluster.put_component_template(name="rollup-al_metrics-settings", body=COMPONENT)

# Create generic template for al_metrics
TEMPLATE = {
    "index_patterns": [
        "rollup-al_metrics*"
    ],
    "composed_of": [
        "rollup-al_metrics-settings"
    ],
    "priority": 100
}
es_client.indices.put_index_template(name="rollup-al_metrics", body=TEMPLATE)

# Create and start rollup jobs
# PUT _rollup/job/<job_id>
# POST _rollup/job/<job_id>/start
ROLLUP_JOBS = [
    {
        "index_pattern": ".ds-al_metrics_es_cluster*",
        "rollup_index": "rollup-al_metrics_es_cluster",
        "cron": CRON,
        "id": "rollup-al_metrics_es_cluster-job",
        "page_size": 1000,
        "groups": {
            "date_histogram": {
                "field": "@timestamp",
                "calendar_interval": INTERVAL
            }
        },
        "metrics": [
            {
                "field": "@timestamp",
                "metrics": ["max", "min", "value_count"]
            },
            {
                "field": "indices.rate.get",
                "metrics": ["avg"]
            },
            {
                "field": "indices.latency.get",
                "metrics": ["avg"]
            },
            {
                "field": "indices.rate.index",
                "metrics": ["avg"]
            },
            {
                "field": "indices.latency.index",
                "metrics": ["avg"]
            },
            {
                "field": "indices.rate.search",
                "metrics": ["avg"]
            },
            {
                "field": "indices.latency.search",
                "metrics": ["avg"]
            },
            {
                "field": "nodes.count",
                "metrics": ["max"]
            },
            {
                "field": "indices.count",
                "metrics": ["max"]
            },
            {
                "field": "indices.shards.unassigned",
                "metrics": ["max"]
            },
            {
                "field": "indices.shards.primary",
                "metrics": ["max"]
            },
            {
                "field": "indices.shards.active",
                "metrics": ["max"]
            },
            {
                "field": "indices.docs.count",
                "metrics": ["max"]
            },
            {
                "field": "indices.docs.size",
                "metrics": ["max"]
            },
            {
                "field": "nodes.heap.total",
                "metrics": ["avg"]
            },
            {
                "field": "nodes.heap.used",
                "metrics": ["avg"]
            },
            {
                "field": "nodes.fs.total",
                "metrics": ["avg"]
            },
            {
                "field": "nodes.fs.used",
                "metrics": ["avg"]
            }
        ]
    },
    {
        "index_pattern": ".ds-al_metrics_archive*",
        "rollup_index": "rollup-al_metrics_archive",
        "id": "rollup-al_metrics_archive-job",
        "cron": CRON,
        "page_size": 1000,
        "groups": {
            "date_histogram": {
                "field": "@timestamp",
                "calendar_interval": INTERVAL
            }
        },
        "metrics": [
            {
                "field": "@timestamp",
                "metrics": ["max", "min", "value_count"]
            },
            {
                "field": "alert",
                "metrics": ["avg"]
            },
            {
                "field": "error",
                "metrics": ["avg"]
            },
            {
                "field": "file",
                "metrics": ["avg"]
            },
            {
                "field": "result",
                "metrics": ["avg"]
            },
            {
                "field": "submission",
                "metrics": ["avg"]
            }
        ]
    },
    {
        "index_pattern": ".ds-al_metrics_expiry*",
        "rollup_index": "rollup-al_metrics_expiry",
        "id": "rollup-al_metrics_expiry-job",
        "cron": CRON,
        "page_size": 1000,
        "groups": {
            "date_histogram": {
                "field": "@timestamp",
                "calendar_interval": INTERVAL
            }
        },
        "metrics": [
            {
                "field": "@timestamp",
                "metrics": ["max", "min", "value_count"]
            },
            {
                "field": "alert",
                "metrics": ["avg"]
            },
            {
                "field": "cached_file",
                "metrics": ["avg"]
            },
            {
                "field": "emptyresult",
                "metrics": ["avg"]
            },
            {
                "field": "error",
                "metrics": ["avg"]
            },
            {
                "field": "file",
                "metrics": ["avg"]
            },
            {
                "field": "filescore",
                "metrics": ["avg"]
            },
            {
                "field": "result",
                "metrics": ["avg"]
            },
            {
                "field": "submission",
                "metrics": ["avg"]
            },
            {
                "field": "submission_summary",
                "metrics": ["avg"]
            },
            {
                "field": "submission_tree",
                "metrics": ["avg"]
            }
        ]
    },
    {
        "index_pattern": ".ds-al_metrics_alerter*",
        "rollup_index": "rollup-al_metrics_alerter",
        "id": "rollup-al_metrics_alerter-job",
        "cron": CRON,
        "page_size": 1000,
        "groups": {
            "date_histogram": {
                "field": "@timestamp",
                "calendar_interval": INTERVAL
            }
        },
        "metrics": [
            {
                "field": "@timestamp",
                "metrics": ["max", "min", "value_count"]
            },
            {
                "field": "created",
                "metrics": ["sum"]
            },
            {
                "field": "updated",
                "metrics": ["sum"]
            }
        ]
    },
    {
        "index_pattern": ".ds-al_metrics_ingester*",
        "rollup_index": "rollup-al_metrics_ingester",
        "id": "rollup-al_metrics_ingester-job",
        "cron": CRON,
        "page_size": 1000,
        "groups": {
            "date_histogram": {
                "field": "@timestamp",
                "calendar_interval": INTERVAL
            }
        },
        "metrics": [
            {
                "field": "@timestamp",
                "metrics": ["max", "min", "value_count"]
            },
            {
                "field": "duplicates",
                "metrics": ["avg", "max"]
            },
            {
                "field": "skipped",
                "metrics": ["avg"]
            },
            {
                "field": "error",
                "metrics": ["avg"]
            },
            {
                "field": "timed_out",
                "metrics": ["avg"]
            },
            {
                "field": "whitelisted",
                "metrics": ["avg"]
            },
            {
                "field": "files_completed",
                "metrics": ["sum", "avg"]
            },
            {
                "field": "submissions_completed",
                "metrics": ["sum", "avg", "max"]
            },
            {
                "field": "submissions_ingested",
                "metrics": ["sum", "avg", "max"]
            }
        ]
    },
    {
        "index_pattern": ".ds-al_metrics_service*",
        "rollup_index": "rollup-al_metrics_service",
        "id": "rollup-al_metrics_service-job",
        "cron": CRON,
        "page_size": 1000,
        "groups": {
            "date_histogram": {
                "field": "@timestamp",
                "calendar_interval": INTERVAL
            },
            "terms": {
                "fields": ["name.keyword"]
            }
        },
        "metrics": [
            {
                "field": "@timestamp",
                "metrics": ["max", "min", "value_count"]
            },
            {
                "field": "execute",
                "metrics": ["sum"]
            },
            {
                "field": "scored",
                "metrics": ["sum"]
            },
            {
                "field": "not_scored",
                "metrics": ["sum"]
            }
        ]
    },
    {
        "index_pattern": ".ds-al_metrics_es_indices*",
        "rollup_index": "rollup-al_metrics_es_indices",
        "cron": CRON,
        "id": "rollup-al_metrics_es_indices-job",
        "page_size": 1000,
        "groups": {
            "date_histogram": {
                "field": "@timestamp",
                "calendar_interval": INTERVAL
            },
            "terms": {
                "fields": ["status.keyword", "name.keyword"]
            }
        },
        "metrics": [
            {
                "field": "@timestamp",
                "metrics": ["max", "min", "value_count"]
            },
            {
                "field": "segments.total",
                "metrics": ["max"]
            },
            {
                "field": "docs.total",
                "metrics": ["sum", "avg", "max", "min"]
            }
        ]
    },
    {
        "index_pattern": ".ds-al_metrics_dispatcher*",
        "rollup_index": "rollup-al_metrics_dispatcher",
        "id": "rollup-al_metrics_dispatcher-job",
        "cron": CRON,
        "page_size": 1000,
        "groups": {
            "date_histogram": {
                "field": "@timestamp",
                "calendar_interval": INTERVAL
            }
        },
        "metrics": [
            {
                "field": "@timestamp",
                "metrics": ["max", "min", "value_count"]
            },
            {
                "field": "files_completed",
                "metrics": ["avg"]
            },
            {
                "field": "submissions_completed",
                "metrics": ["avg"]
            }
        ]
    },
    {
        "index_pattern": ".ds-al_metrics*",
        "rollup_index": "rollup-al_metrics",
        "id": "rollup-al_metrics-job",
        "cron": CRON,
        "page_size": 1000,
        "groups": {
            "date_histogram": {
                "field": "@timestamp",
                "calendar_interval": INTERVAL
            }
        },
        "metrics": [
            {
                "field": "@timestamp",
                "metrics": ["max", "min", "value_count"]
            },
            {
                "field": "submissions_completed",
                "metrics": ["sum", "max"]
            },
            {
                "field": "submissions_ingested",
                "metrics": ["sum", "max"]
            },
            {
                "field": "skipped",
                "metrics": ["sum", "max"]
            },
            {
                "field": "created",
                "metrics": ["sum", "max"]
            },
            {
                "field": "duplicates",
                "metrics": ["sum", "max"]
            }
        ]
    },
    {
        "index_pattern": ".ds-al_metrics_scaler_status*",
        "rollup_index": "rollup-al_metrics_scaler_status",
        "id": "rollup-al_metrics_scaler_status-job",
        "cron": CRON,
        "page_size": 1000,
        "groups": {
            "date_histogram": {
                "field": "@timestamp",
                "calendar_interval": INTERVAL
            }
        },
        "metrics": [
            {
                "field": "@timestamp",
                "metrics": ["max", "min", "value_count"]
            },
            {
                "field": "running",
                "metrics": ["max", "min", "avg"]
            },
            {
                "field": "queue",
                "metrics": ["max", "min", "avg"]
            }
        ]
    }
]
for job in ROLLUP_JOBS:
    es_client.rollup.put_job(id=job['id'], body=job)
    # es_client.rollup.start_job(id)(id=job['id'])

print("Done")
