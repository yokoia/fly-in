*This project has been created as part of the 42 curriculum by <ykoia>.*

# Fly-In

## Description

Fly-In is a Python drone traffic simulation.

The goal is to move all drones from a start hub to an end hub in
    as few simulation turns as possible while respecting:

- Hub capacities
- Connection capacities
- Blocked zones
- Restricted zones
- Priority zones

The program parses a map, builds a network, finds routes,
    assigns drones to those routes, and simulates all drone movements turn by turn.

## Instructions

Python 3.10 or later is required.

Run the project with:

```bash
make run MAP=<map_file>