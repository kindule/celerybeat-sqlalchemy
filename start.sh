#!/usr/bin/env bash
celery beat -S beatsqlalchemy.schedulers.DatabaseScheduler