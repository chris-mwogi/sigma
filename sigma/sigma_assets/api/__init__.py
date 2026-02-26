# Sigma Integrations API Module
#
# ⚠️ DEPRECATED: iot_asset_integration.py has been removed.
# All IoT integration functionality has been migrated to monitoring_ingestion.py
#
# Migration Guide:
# - iot_alert_webhook() → monitoring_ingestion.receive_webhook()
# - link_asset_event_to_case() → monitoring_ingestion.link_monitoring_alert_to_case()
# - get_iot_device_status() → monitoring_ingestion.get_device_monitoring_info()
# - get_iot_alerts() → monitoring_ingestion.get_device_monitoring_info()
# - update_device_heartbeat() → Webhook auto-updates last_seen
# - decommission_iot_device() → Update Monitored Device.status directly
#
# See: sigma.sigma_assets.api.monitoring_ingestion

__all__ = []

