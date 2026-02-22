# Computational Judicial Decision Simulation

## Abstract

This project presents a computational framework for modeling judicial decision-making processes across civil and criminal law domains. The system integrates rule-based legal reasoning mechanisms for civil law cases and discretionary, score-based evaluation models for criminal law scenarios. The objective is to simulate structured judicial reasoning while preserving domain-specific constraints and decision flexibility.

## Motivation

Judicial reasoning involves a combination of deterministic legal rules and discretionary judgment. This project explores how computational models can replicate these dual characteristics through:

- Deterministic rule-constrained reasoning (civil law)
- Weighted discretionary scoring mechanisms (criminal law)
- Structured case input processing
- Legal text and precedent referencing

## System Architecture

The project follows a modular architecture:

- `app/decision/` → Civil and criminal reasoning engines  
- `app/services/` → Decision orchestration layer  
- `app/retrieval/` → Legal reference retrieval  
- `app/db/` → Persistence and case storage  
- `app/templates/` → Web interface  

## Methodology

### Civil Law Module
Implements deterministic legal rule evaluation based on predefined statutory mappings and condition validation.

### Criminal Law Module
Implements weighted scoring logic reflecting discretionary judicial authority, including mitigating and aggravating factor modeling.

### Legal Reference System
Structured JSON-based legal corpus enabling citation and decision support logic.

## Technologies

- Python
- FastAPI
- Jinja2
- SQLAlchemy
- Structured JSON Legal Data

## Research Perspective

This system serves as an experimental framework for:
- Computational legal reasoning
- AI-assisted judicial modeling
- Hybrid deterministic-discretionary decision systems

## Author

Merve Sencak  
2026
