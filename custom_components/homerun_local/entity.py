"""Shared base entity for the Philips HomeRun (Local) integration."""

from __future__ import annotations

import time

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import HomeRunCoordinator
from .const import DOMAIN, MANUFACTURER, MODEL


class HomeRunEntity(CoordinatorEntity[HomeRunCoordinator]):
    """Base entity tying everything to a single device."""

    _attr_has_entity_name = True

    # Entities that show the robot's own values go unavailable once the backend
    # hasn't heard from it for this long (LAN connection lost, address changed),
    # instead of showing the last values as if they were current. The map camera
    # and floor select come from the cloud and opt out.
    ROBOT_STALE_AFTER = 180
    _requires_robot = True

    def __init__(self, coordinator: HomeRunCoordinator) -> None:
        super().__init__(coordinator)
        entry = coordinator.entry
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Philips HomeRun",
            manufacturer=MANUFACTURER,
            model=(coordinator.diagnostics.get("capabilities") or {}).get("model")
            or MODEL,
            configuration_url=coordinator.client.base_url,
        )

    @property
    def available(self) -> bool:
        if not super().available:
            return False
        d = self.data
        if not self._requires_robot or d.get("source") != "robot":
            return True
        return bool(d.get("connected")) or time.time() - (d.get("last_update") or 0) < self.ROBOT_STALE_AFTER

    @property
    def data(self) -> dict:
        """Latest state object from the coordinator (never None after setup)."""
        return self.coordinator.data or {}

    @property
    def diag(self) -> dict:
        """Latest diagnostics blob (consumables, toggles, totals, faults)."""
        return self.coordinator.diagnostics or {}
