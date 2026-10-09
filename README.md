# ⚡ Smart Energy Efficiency and Automated Control System for University Lecture Rooms

> An intelligent, IoT-driven automation platform built on Raspberry Pi to eliminate idle power waste and optimize energy efficiency in university lecture halls.

[![Platform](https://img.shields.io/badge/Platform-Raspberry%20Pi-C51A4A?logo=raspberry-pi&logoColor=white)](#)
[![Domain](https://img.shields.io/badge/Domain-IoT%20%7C%20Energy%20Efficiency-007ACC)](#)
[![Status](https://img.shields.io/badge/Status-Prototype%20Development-success)](#)
[![License](https://img.shields.io/badge/License-MIT-green)](#)

---

## 📌 Problem Statement

University lecture rooms can consume significant amounts of electrical energy through lighting, fans, air conditioning, and other electrical equipment. These systems often remain switched on when a room is empty or only partially occupied, and frequently operate at full capacity regardless of the number of students present or prevailing environmental conditions.

This unnecessary energy consumption increases operating costs and contributes to inefficient use of electricity. Because different groups of students and lecturers rotate through lecture rooms throughout the day, manually monitoring and controlling equipment is difficult and unreliable. An automated system is therefore needed to monitor room occupancy and environmental conditions, eliminate unnecessary energy waste, and maintain an ergonomic learning environment.

---

## 💡 Proposed Solution

This project implements a Raspberry Pi-based smart energy-efficiency system for university lecture halls. The Raspberry Pi serves as the main processing and control unit, interfacing with environmental and occupancy sensors:

- **Occupancy Automation:** Automatically shuts down electrical loads when no occupants are detected after an established cooldown period.
- **Daylight Harvesting:** Uses ambient light measurements to modulate artificial lighting, preventing unnecessary light use when daylight is sufficient.
- **Thermal Comfort Automation:** Activates ventilation fans only when both occupancy and temperature thresholds are met.
- **Power Telemetry & Logging:** Measures real-time electrical current and power, logging time-series records to verify and evaluate energy savings.

---

## 🎯 Project Objectives

1. **Monitor Room Occupancy:** Accurately detect human presence and determine room usage states using motion sensing.
2. **Environmental Tracking:** Measure ambient environmental parameters including temperature, humidity, and light levels.
3. **Automated Load Actuation:** Control electrical loads (lighting and fans) dynamically via relays based on occupancy and sensor inputs.
4. **Energy Measurement:** Continuously monitor load current, voltage, and power consumption using a dedicated energy sensor.
5. **Data Logging:** Record time-stamped environmental and electrical data for historical analysis and reporting.
6. **Energy Savings Verification:** Quantify real energy reduction by evaluating power profiles before and after automated control.
7. **Cost-Effective Prototyping:** Build a low-cost, scalable demonstration unit applicable to campus-wide facility management.

---

## 🏗️ System Architecture

```text
 ┌────────────────────────────────────────────────────────┐
 │                    SENSOR LAYER                        │
 │  [PIR Motion]    [LDR Lux Sensor]    [DHT22 Temp/Hum]  │
 └────────┬─────────────────┬────────────────────┬────────┘
          │                 │                    │
          ▼                 ▼                    ▼
 ┌────────────────────────────────────────────────────────┐
 │           EDGE CONTROLLER (Raspberry Pi)               │
 │   • State Machine & Automation Logic                   │
 │   • Current/Power Measurement (INA219 / ACS712)        │
 │   • Telemetry Logging & Data Dashboard                 │
 └──────────────────────────┬─────────────────────────────┘
                            │ (GPIO / Relay Triggers)
                            ▼
 ┌────────────────────────────────────────────────────────┐
 │                    ACTUATION LAYER                     │
 │  [Relay Board] ──> [LED Lighting]  [Ventilation Fans]  │
 └────────────────────────────────────────────────────────┘
