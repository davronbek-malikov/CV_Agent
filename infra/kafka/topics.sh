#!/bin/sh
# Creates every Darvoza topic. Safe to run more than once.
set -e
BS="${KAFKA_BOOTSTRAP:-kafka:9092}"
KT=/opt/kafka/bin/kafka-topics.sh

create() {
  $KT --bootstrap-server "$BS" --create --if-not-exists --topic "$1" --partitions 3 --replication-factor 1 \
      --config retention.ms="$2" >/dev/null
  echo "topic ready: $1"
}

DAY=86400000
create user.requests   $((3 * DAY))
create agent.tasks     $((3 * DAY))
create agent.results   $((3 * DAY))
create judge.verdicts  $((3 * DAY))
create agent.events    $DAY
create session.replies $DAY
create jobs.raw        $((7 * DAY))
create jobs.clean      $((7 * DAY))
create jobs.ready      $((7 * DAY))
create agent.dlq       $((7 * DAY))
