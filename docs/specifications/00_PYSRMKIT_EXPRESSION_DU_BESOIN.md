# PySRMKit — Expression du besoin

**Document :** `00_PYSRMKIT_EXPRESSION_DU_BESOIN.md`  
**Projet :** PySRMKit  
**Domaine :** Supplier Relationship Management  
**Type :** Bibliothèque / Framework métier Python  
**Statut :** Expression initiale du besoin  
**Version du document :** 0.1.0

---

# 1. Introduction

Les entreprises entretiennent des relations structurées avec plusieurs catégories de parties prenantes :

- leurs clients ;
- leurs fournisseurs ;
- leurs collaborateurs ;
- leurs partenaires ;
- leurs investisseurs ;
- leurs administrations ;
- leurs sous-traitants.

Alors que la relation client est largement structurée autour des systèmes de **Customer Relationship Management — CRM**, la relation fournisseur repose sur un ensemble de concepts généralement regroupés sous les termes :

- Supplier Relationship Management — SRM ;
- Supplier Management ;
- Supplier Lifecycle Management — SLM ;
- Supplier Information Management — SIM ;
- Supplier Performance Management — SPM ;
- Supplier Risk Management ;
- Supplier Qualification ;
- Supplier Onboarding.

Ces fonctions sont souvent intégrées dans de grandes plateformes Source-to-Pay telles que Ivalua, Coupa, SAP Ariba ou Jaggaer.

Cependant, dans les architectures logicielles modernes, il peut être pertinent de disposer d'un **noyau métier SRM indépendant**, réutilisable et agnostique vis-à-vis :

- de l'ERP ;
- du moteur de workflow ;
- de la base de données ;
- de l'interface utilisateur ;
- du fournisseur cloud ;
- du système comptable ;
- du système Procurement ;
- du moteur documentaire ;
- des plateformes externes de conformité.

**PySRMKit** a vocation à constituer ce noyau.

---

# 2. Vision générale

PySRMKit est une bibliothèque Python destinée à représenter, manipuler et orchestrer les concepts fondamentaux de la **gestion de la relation fournisseur**.

Son objectif est de fournir un domaine métier réutilisable permettant à une application de répondre notamment aux questions suivantes :

> Qui sont nos fournisseurs ?

> Avec quelles entités juridiques travaillons-nous ?

> Quels produits, services ou catégories d'achat peuvent-ils fournir ?

> Où en sont-ils dans leur processus d'onboarding ?

> Sont-ils qualifiés pour travailler avec l'organisation ?

> Quels documents et certifications leur avons-nous demandés ?

> Quels risques leur sont associés ?

> Comment leurs performances évoluent-elles ?

> Quels incidents ont été rencontrés ?

> Quels fournisseurs sont actifs, suspendus ou déréférencés ?

> Quelle est l'histoire complète de notre relation avec eux ?

PySRMKit doit ainsi jouer pour le **Supplier Domain** un rôle comparable à celui qu'un CRM joue pour le Customer Domain.

---

# 3. Problématique

Dans de nombreux systèmes d'information, le concept de fournisseur est réduit à une fiche relativement pauvre contenant :

- une raison sociale ;
- une adresse ;
- un numéro fiscal ;
- des coordonnées bancaires ;
- quelques contacts ;
- un identifiant ERP.

Cette représentation est insuffisante.

Un fournisseur est en réalité une entité métier possédant :

- une identité juridique ;
- plusieurs établissements ;
- plusieurs contacts ;
- plusieurs catégories d'activité ;
- plusieurs capacités opérationnelles ;
- différents niveaux de qualification ;
- des certifications ;
- des documents contractuels ;
- des risques ;
- des évaluations ;
- un historique de performance ;
- des incidents ;
- des engagements ;
- des relations commerciales dans le temps.

La gestion de ces informations est souvent dispersée entre :

```text
ERP
+
Procurement
+
Comptabilité
+
Emails
+
Documents
+
Excel
+
Workflow
+
Risk Management
+
Contract Management
```

Cette fragmentation entraîne plusieurs difficultés :

- duplication des données ;
- incohérences entre systèmes ;
- absence de modèle fournisseur canonique ;
- onboarding difficile à suivre ;
- contrôles de conformité manuels ;
- manque de traçabilité ;
- difficulté à évaluer la performance ;
- dépendance forte à une solution SRM propriétaire ;
- complexité des intégrations ;
- difficulté à réutiliser les règles métier.

---

# 4. Besoin principal

Le besoin consiste à construire un **noyau métier Python générique pour la gestion des fournisseurs**.

Ce noyau devra couvrir le cycle de vie complet d'un fournisseur :

```text
DISCOVERED
     │
     ▼
PROSPECTIVE
     │
     ▼
INVITED
     │
     ▼
ONBOARDING
     │
     ▼
UNDER_REVIEW
     │
     ▼
QUALIFIED
     │
     ▼
ACTIVE
     │
     ├──────────► SUSPENDED
     │
     ├──────────► BLOCKED
     │
     ▼
INACTIVE
     │
     ▼
OFFBOARDED
```

Le framework devra gérer aussi bien :

- les informations du fournisseur ;
- son onboarding ;
- sa qualification ;
- son suivi ;
- son évaluation ;
- sa conformité ;
- ses risques ;
- ses performances ;
- son historique relationnel.

---

# 5. Objectif produit

L'objectif de PySRMKit est de devenir une brique métier indépendante permettant de construire différents types de systèmes :

```text
PySRMKit
   │
   ├── Supplier Portal
   │
   ├── Procurement Platform
   │
   ├── ERP
   │
   ├── Source-to-Pay Platform
   │
   ├── Supplier Risk Platform
   │
   ├── Marketplace B2B
   │
   ├── Vendor Management System
   │
   ├── Contract Management Platform
   │
   └── Agentic Enterprise Platform
```

PySRMKit ne doit donc pas être une application SRM complète.

Il constitue le **domain engine** sur lequel ces applications peuvent être construites.

---

# 6. Principe fondamental

PySRMKit doit représenter le fournisseur comme un **agrégat métier riche**, et non comme une simple ligne de table.

```text
Supplier
│
├── Identity
│
├── Legal Entity
│
├── Locations
│
├── Contacts
│
├── Categories
│
├── Capabilities
│
├── Documents
│
├── Certifications
│
├── Qualification
│
├── Compliance
│
├── Risks
│
├── Assessments
│
├── Performance
│
├── Incidents
│
├── Relationships
│
└── Lifecycle
```

---

# 7. Positionnement fonctionnel

PySRMKit doit couvrir le domaine :

> **Supplier Relationship Management**

et non l'ensemble de la chaîne achat.

Il doit donc clairement distinguer :

```text
SRM
Supplier Relationship Management
```

de :

```text
PROCUREMENT
Purchase Requisition
Sourcing
RFQ
RFP
Purchase Order
Goods Receipt
```

et de :

```text
P2P
Procure-to-Pay
```

et de :

```text
AP
Accounts Payable
Invoice
Payment
Settlement
```

---

# 8. Frontières du domaine

## 8.1 Dans PySRMKit

PySRMKit doit notamment couvrir :

- Supplier Identity ;
- Supplier Organization ;
- Supplier Lifecycle ;
- Supplier Contacts ;
- Supplier Locations ;
- Supplier Categories ;
- Supplier Capabilities ;
- Supplier Qualification ;
- Supplier Onboarding ;
- Supplier Documents ;
- Supplier Certifications ;
- Supplier Compliance ;
- Supplier Assessments ;
- Supplier Performance ;
- Supplier Risk ;
- Supplier Incidents ;
- Supplier Segmentation ;
- Supplier Status ;
- Supplier Relationships ;
- Supplier Scorecards.

---

## 8.2 Hors du cœur PySRMKit

PySRMKit ne doit pas directement prendre en charge :

- Purchase Orders ;
- Purchase Requisitions ;
- RFQ / RFP ;
- appels d'offres ;
- factures ;
- paiements ;
- comptabilité fournisseur ;
- gestion générale des contrats ;
- stockage physique des documents ;
- authentification ;
- workflow générique ;
- orchestration technique ;
- notifications ;
- reporting BI.

Ces fonctions pourront appartenir à d'autres composants.

Exemple :

```text
PySRMKit
    Supplier Domain

PyProcurementKit
    Procurement Domain

PyContractKit
    Contract Domain

PyAccountingKit
    Accounting Domain

PyIAMKit
    Identity & Access

PyWorkflowKit
    Workflow Orchestration

PyScheduleKit
    Scheduling

PyRuntimeKit
    Execution Runtime
```

---

# 9. Entités métier principales envisagées

Le domaine initial devra pouvoir représenter les concepts suivants.

## Supplier

Entité fournisseur principale.

```text
Supplier
├── id
├── code
├── legal_name
├── trading_name
├── status
├── lifecycle_stage
├── supplier_type
├── categories
├── identifiers
├── contacts
├── locations
└── metadata
```

---

## SupplierOrganization

Représentation organisationnelle d'un fournisseur.

Elle pourra notamment permettre de gérer :

- maison mère ;
- filiale ;
- établissement ;
- branche ;
- groupe ;
- organisation liée.

---

## SupplierContact

Personne de contact associée au fournisseur.

Exemples :

- commercial ;
- direction ;
- comptabilité ;
- support ;
- conformité ;
- juridique ;
- responsable de compte.

---

## SupplierLocation

Établissement ou site fournisseur.

Exemples :

- siège social ;
- usine ;
- agence ;
- entrepôt ;
- bureau ;
- centre logistique.

---

## SupplierCategory

Catégorisation des fournisseurs.

Exemples :

```text
IT
Consulting
Construction
Maintenance
Energy
Facilities
Transport
Professional Services
Software
Telecommunications
```

---

## SupplierCapability

Capacité déclarée ou vérifiée d'un fournisseur.

Exemple :

```text
Supplier
    │
    ├── Cloud Consulting
    ├── Python Development
    ├── Data Engineering
    └── Managed Services
```

---

# 10. Supplier Lifecycle

Le cycle de vie du fournisseur constitue l'un des concepts centraux de PySRMKit.

Exemple de lifecycle :

```text
PROSPECTIVE
     │
     ▼
INVITED
     │
     ▼
ONBOARDING
     │
     ▼
UNDER_REVIEW
     │
     ├────► REJECTED
     │
     ▼
QUALIFIED
     │
     ▼
ACTIVE
     │
     ├────► SUSPENDED
     │
     ├────► BLOCKED
     │
     ▼
INACTIVE
     │
     ▼
OFFBOARDED
```

La machine à états devra être configurable.

---

# 11. Supplier Onboarding

PySRMKit devra permettre de modéliser un processus d'intégration fournisseur.

L'onboarding pourra inclure :

```text
Supplier Invitation
        │
        ▼
Identity Collection
        │
        ▼
Company Information
        │
        ▼
Legal Information
        │
        ▼
Tax Information
        │
        ▼
Bank Information Reference
        │
        ▼
Document Collection
        │
        ▼
Compliance Checks
        │
        ▼
Qualification
        │
        ▼
Approval
        │
        ▼
Activation
```

PySRMKit devra représenter l'état métier du processus sans imposer le moteur technique utilisé pour son orchestration.

---

# 12. Supplier Qualification

Un fournisseur ne doit pas nécessairement être autorisé à fournir n'importe quel produit ou service.

La qualification pourra être définie selon :

- catégorie d'achat ;
- pays ;
- organisation ;
- business unit ;
- type de prestation ;
- seuil financier ;
- niveau de risque.

Exemple :

```text
Supplier: ACME Consulting

Qualification
├── IT Consulting       QUALIFIED
├── Cloud Services      QUALIFIED
├── Cybersecurity       PENDING
└── Construction        NOT_QUALIFIED
```

---

# 13. Supplier Documents

Le système devra pouvoir référencer les documents nécessaires à la gestion du fournisseur.

Exemples :

- extrait d'immatriculation ;
- attestation fiscale ;
- attestation sociale ;
- assurance ;
- RIB ;
- certifications ;
- licences ;
- attestations réglementaires ;
- politique ESG ;
- documents de conformité.

PySRMKit ne devra pas obligatoirement stocker les fichiers eux-mêmes.

Il devra pouvoir manipuler une abstraction :

```text
SupplierDocument
├── type
├── reference
├── issue_date
├── expiration_date
├── verification_status
├── issuer
└── storage_reference
```

---

# 14. Supplier Certification

PySRMKit devra pouvoir gérer les certifications du fournisseur.

Exemples :

```text
ISO 9001
ISO 27001
ISO 14001
SOC 2
EcoVadis
Professional Licenses
```

Chaque certification pourra comporter :

- autorité émettrice ;
- date d'émission ;
- date d'expiration ;
- périmètre ;
- statut ;
- preuve documentaire.

---

# 15. Supplier Compliance

Le domaine devra permettre de représenter différentes obligations de conformité.

Exemples :

- conformité juridique ;
- conformité fiscale ;
- sanctions internationales ;
- KYS — Know Your Supplier ;
- obligations sociales ;
- conformité ESG ;
- conformité cybersécurité ;
- protection des données ;
- assurance professionnelle.

Le moteur ne devra pas imposer les fournisseurs de données utilisés pour effectuer ces vérifications.

---

# 16. Supplier Risk Management

PySRMKit devra pouvoir représenter les risques associés à un fournisseur.

Exemples :

```text
Supplier Risk
│
├── Financial Risk
├── Operational Risk
├── Cyber Risk
├── Compliance Risk
├── ESG Risk
├── Geopolitical Risk
├── Supply Chain Risk
├── Concentration Risk
└── Reputational Risk
```

Un fournisseur pourra posséder plusieurs évaluations de risque dans le temps.

---

# 17. Supplier Assessment

Le framework devra permettre de réaliser différents types d'évaluations.

Exemples :

- questionnaire fournisseur ;
- audit ;
- évaluation métier ;
- revue de conformité ;
- revue annuelle ;
- revue de risque ;
- auto-évaluation.

Structure conceptuelle :

```text
Assessment
├── assessment_type
├── supplier
├── questions
├── answers
├── scores
├── reviewers
├── evidence
└── decision
```

---

# 18. Supplier Performance

La performance fournisseur devra être modélisée comme une série d'indicateurs mesurables.

Exemples :

```text
Delivery Performance
Quality
Service Level
Cost
Responsiveness
Innovation
Compliance
Sustainability
Incident Rate
```

Un modèle de scorecard pourra agréger plusieurs métriques.

```text
Supplier Scorecard
│
├── Quality              91/100
├── Delivery             86/100
├── Cost                 78/100
├── Compliance           100/100
├── ESG                  83/100
│
└── Overall Score        87/100
```

---

# 19. Supplier Incident Management

PySRMKit devra pouvoir référencer les événements négatifs associés à un fournisseur.

Exemples :

- retard ;
- livraison non conforme ;
- problème qualité ;
- violation contractuelle ;
- incident de sécurité ;
- fraude ;
- interruption de service ;
- non-conformité réglementaire.

Un incident pourra influencer :

- le score fournisseur ;
- son niveau de risque ;
- sa qualification ;
- son statut.

---

# 20. Supplier Segmentation

Les fournisseurs pourront être segmentés.

Exemples classiques :

```text
Strategic
Critical
Preferred
Approved
Standard
Transactional
Restricted
```

La segmentation pourra dépendre notamment :

- du volume d'achat ;
- de la criticité ;
- de la dépendance ;
- du risque ;
- de la performance ;
- de la substituabilité du fournisseur.

---

# 21. Supplier Relationship

PySRMKit devra pouvoir représenter une relation commerciale indépendamment de l'existence juridique du fournisseur.

Une même organisation pourra par exemple avoir :

```text
ACME GROUP
│
├── ACME France
│   └── Supplier Relationship — France
│
├── ACME Germany
│   └── Supplier Relationship — Germany
│
└── ACME UK
    └── Supplier Relationship — UK
```

Cela permet de distinguer :

```text
Who the supplier is
```

de :

```text
How our organization works with the supplier
```

---

# 22. Supplier Master Data

PySRMKit devra permettre la création d'un modèle fournisseur canonique pouvant alimenter ou être alimenté par plusieurs systèmes.

```text
                  PySRMKit
                      │
        ┌─────────────┼─────────────┐
        │             │             │
       ERP       Procurement      CRM
        │             │             │
        └─────────────┼─────────────┘
                      │
                 Data Platform
```

Il devra être possible de stocker des identifiants externes :

```text
ERP_VENDOR_ID
IVALUA_SUPPLIER_ID
SAP_VENDOR_ID
DUNS
SIREN
SIRET
VAT_NUMBER
INTERNAL_REFERENCE
```

sans que ces identifiants deviennent l'identité métier fondamentale de l'entité.

---

# 23. Cas d'usage fondamentaux

PySRMKit devra permettre des cas d'utilisation tels que :

## Création

```python
supplier = Supplier.create(...)
```

## Enregistrement

```python
supplier.register()
```

## Invitation

```python
supplier.invite()
```

## Démarrage onboarding

```python
supplier.start_onboarding()
```

## Qualification

```python
supplier.qualify(category="IT_SERVICES")
```

## Activation

```python
supplier.activate()
```

## Suspension

```python
supplier.suspend(reason="COMPLIANCE_REVIEW")
```

## Evaluation

```python
assessment = supplier.create_assessment(...)
```

## Enregistrement d'un risque

```python
supplier.register_risk(...)
```

## Performance

```python
supplier.record_performance(...)
```

## Incident

```python
supplier.report_incident(...)
```

Les exemples ci-dessus illustrent uniquement la sémantique métier recherchée et ne constituent pas encore une API définitive.

---

# 24. Domain Events

Les changements importants du domaine devront pouvoir produire des événements métier.

Exemples :

```text
SupplierCreated
SupplierRegistered
SupplierInvited
SupplierOnboardingStarted
SupplierInformationUpdated
SupplierDocumentSubmitted
SupplierDocumentExpired
SupplierQualificationRequestedSupplierQualified
SupplierQualificationRejected
SupplierActivated
SupplierSuspended
SupplierBlocked
SupplierReactivated
SupplierRiskDetected
SupplierRiskChanged
SupplierAssessmentCompleted
SupplierPerformanceRecorded
SupplierIncidentReported
SupplierOffboarded
```

Ces événements permettront l'intégration avec d'autres systèmes sans créer de dépendance directe.

---

# 25. Architecture d'intégration cible

PySRMKit devra pouvoir fonctionner dans une architecture évènementielle.

```text
                    PySRMKit
                       │
                Domain Events
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
 Procurement      Accounting       Contract
        │              │              │
        ▼              ▼              ▼
PyProcurementKit PyAccountingKit PyContractKit
```

Exemple :

```text
SupplierActivated
        │
        ├──► Procurement
        │      Supplier can receive POs
        │
        ├──► Accounting
        │      Vendor account may be created
        │
        └──► Contract Management
               Contracts may become active
```

---

# 26. Agnosticisme technologique

PySRMKit ne devra imposer :

- aucun ORM ;
- aucune base de données ;
- aucun framework Web ;
- aucun fournisseur cloud ;
- aucun système de message ;
- aucun moteur de workflow ;
- aucun système IAM ;
- aucun système documentaire.

L'utilisation devra être possible depuis :

```text
FastAPI
Django
Flask
CLI
Worker
Notebook
Agent
Batch
Microservice
Serverless Function
```

---

# 27. Persistence Agnostic

Le domaine devra être indépendant de la persistence.

Les implémentations pourront utiliser :

```text
PostgreSQL
MySQL
SQLite
MongoDB
DynamoDB
Snowflake
In-memory
```

La persistence devra passer par des interfaces ou ports dédiés.

---

# 28. Workflow Agnostic

PySRMKit devra définir les transitions métier sans devenir lui-même un moteur de workflow générique.

Par exemple :

```text
PySRMKit
    defines:
        Supplier can be qualified

PyWorkflowKit
    decides:
        who must approve
        in what order
        with what timeout
```

---

# 29. Integration Agnostic

Les intégrations externes devront être réalisées à travers des ports.

Exemples :

```text
CompanyRegistryProvider
TaxValidationProvider
SanctionsScreeningProvider
BankVerificationProvider
DocumentStorageProvider
NotificationProvider
RiskDataProvider
ERPProvider
ProcurementProvider
```

---

# 30. Extensibilité

Un objectif essentiel de PySRMKit est de permettre l'ajout de règles métier spécifiques sans modifier le noyau.

Par exemple :

```python
qualification_policy.evaluate(supplier)
```

pourra être remplacée par une politique propre à l'organisation.

De même :

```text
RiskPolicy
QualificationPolicy
ActivationPolicy
SegmentationPolicy
CompliancePolicy
PerformancePolicy
```

devront être extensibles.

---

# 31. Multi-organisation

PySRMKit devra pouvoir être utilisé dans des organisations complexes.

Exemple :

```text
GROUP
│
├── Subsidiary A
│   ├── Supplier 1
│   └── Supplier 2
│
├── Subsidiary B
│   ├── Supplier 1
│   └── Supplier 3
│
└── Subsidiary C
```

Un même fournisseur pourra avoir des relations différentes avec plusieurs entités internes.

---

# 32. Multi-pays

Le framework devra être capable de gérer des fournisseurs internationaux.

Les concepts suivants devront donc être extensibles :

- types d'identifiants ;
- formats fiscaux ;
- adresses ;
- obligations réglementaires ;
- documents ;
- devises ;
- langues.

Le domaine ne devra pas être conçu exclusivement autour du modèle français.

---

# 33. Historisation

Le système devra permettre de reconstruire l'évolution d'un fournisseur.

Exemple :

```text
2026-01-15  Supplier Created
2026-01-16  Onboarding Started
2026-01-20  Documents Submitted
2026-01-22  Compliance Approved
2026-01-25  Supplier Qualified
2026-02-01  Supplier Activated
2026-06-10  Performance Review
2026-09-15  Risk Increased
2026-09-20  Supplier Suspended
2026-10-01  Supplier Reactivated
```

La traçabilité constitue une exigence importante du domaine.

---

# 34. Auditabilité

Les actions critiques devront pouvoir produire des traces permettant de connaître :

```text
WHAT happened?
WHO initiated it?
WHEN?
WHY?
FROM which state?
TO which state?
WITH which evidence?
```

Cette exigence est particulièrement importante pour :

- onboarding ;
- qualification ;
- conformité ;
- suspension ;
- blocage ;
- réactivation ;
- modification d'informations sensibles.

---

# 35. Interopérabilité

PySRMKit devra pouvoir échanger des données avec des systèmes externes via des représentations standardisées.

Le framework devra faciliter :

- sérialisation ;
- désérialisation ;
- mapping ;
- imports ;
- exports ;
- API ;
- événements ;
- synchronisation.

Il ne devra cependant pas définir directement la couche HTTP.

---

# 36. Relation avec PyProcurementKit

La frontière conceptuelle doit rester claire.

```text
PySRMKit
    WHO can we buy from?

PyProcurementKit
    WHAT do we want to buy?
    HOW do we buy it?
```

Exemple :

```text
Supplier
   │
   ▼
Qualified Supplier
   │
   ▼
PyProcurementKit
   │
   ▼
RFQ
   │
   ▼
Purchase Order
```

---

# 37. Relation avec PyAccountingKit

PyAccountingKit pourra consommer certaines informations issues de PySRMKit.

```text
Supplier
    │
    ▼
Vendor Account
    │
    ▼
Accounts Payable
```

Cependant :

```text
Supplier != Vendor Ledger Account
```

Le fournisseur est une entité commerciale.

Le compte fournisseur est une représentation comptable de cette relation.

---

# 38. Relation avec PyContractKit

Un fournisseur peut avoir plusieurs contrats.

```text
Supplier
│
├── Contract A
├── Contract B
└── Contract C
```

PySRMKit devra pouvoir référencer ces relations sans absorber l'ensemble du domaine contractuel.

---

# 39. Relation avec PyCRMKit

PyCRMKit et PySRMKit représentent deux faces symétriques du système d'entreprise.

```text
                    ORGANIZATION
                         │
            ┌────────────┴────────────┐
            │                         │
         CUSTOMERS                 SUPPLIERS
            │                         │
        PyCRMKit                  PySRMKit
            │                         │
          SALES                   PROCUREMENT
```

Conceptuellement :

```text
CRM
    manages demand-side relationships.

SRM
    manages supply-side relationships.
```

---

# 40. Relation avec Synqentra

Dans une plateforme d'entreprise agentique telle que Synqentra, PySRMKit pourrait devenir le moteur métier du domaine fournisseur.

```text
                    General Agent
                         │
                 Procurement Manager
                         │
       ┌─────────────────┼──────────────────┐
       │                 │                  │
 Supplier Agent    Sourcing Agent     Contract Agent
       │
       ▼
   PySRMKit
```

Un agent pourrait alors utiliser le domaine pour :

- rechercher les fournisseurs éligibles ;
- détecter les documents expirés ;
- surveiller les risques ;
- demander une réévaluation ;
- préparer une revue fournisseur ;
- comparer les performances ;
- déclencher un onboarding ;
- proposer une suspension ;
- expliquer pourquoi un fournisseur n'est pas qualifié.

L'agent ne doit cependant jamais remplacer les invariants métier du domaine.

```text
Agent
   │
   ▼
Application Layer
   │
   ▼
PySRMKit
   │
   ▼
Business Rules
```

---

# 41. Architecture conceptuelle cible

```text
┌───────────────────────────────────────────────────────────┐
│                    Applications                           │
│                                                           │
│ Supplier Portal │ Procurement │ ERP │ Agents │ APIs      │
└─────────────────────────────┬─────────────────────────────┘
                              │
                              ▼
┌───────────────────────────────────────────────────────────┐
│                   Application Layer                       │
│                                                           │
│ Commands │ Queries │ Use Cases │ Policies                │
└─────────────────────────────┬─────────────────────────────┘
                              │
                              ▼
┌───────────────────────────────────────────────────────────┐
│                      PySRMKit                              │
│                                                           │
│ Supplier                                                  │
│ Supplier Lifecycle                                        │
│ Qualification                                             │
│ Onboarding                                                │
│ Compliance                                                │
│ Risk                                                      │
│ Performance                                               │
│ Assessments                                               │
│ Incidents                                                 │
│ Relationships                                             │
│ Domain Events                                             │
└─────────────────────────────┬─────────────────────────────┘
                              │
                              ▼
┌───────────────────────────────────────────────────────────┐
│                        Ports                              │
│                                                           │
│ Repository │ Registry │ Risk │ Documents │ Events        │
└─────────────────────────────┬─────────────────────────────┘
                              │
                              ▼
┌───────────────────────────────────────────────────────────┐
│                       Adapters                            │
│                                                           │
│ PostgreSQL │ Ivalua │ SAP │ REST │ Kafka │ S3 │ etc.   │
└───────────────────────────────────────────────────────────┘
```

---

# 42. Principes structurants

PySRMKit devra respecter plusieurs principes fondamentaux.

## Domain-first

Le modèle métier doit être indépendant des outils.

## Explicit business rules

Les règles importantes doivent être explicites.

## State machines

Les changements de statut doivent être contrôlés.

## Auditability

Les décisions métier doivent être traçables.

## Composability

Les fonctionnalités doivent pouvoir être utilisées indépendamment.

## Extensibility

Les organisations doivent pouvoir définir leurs propres politiques.

## Technology agnostic

Le cœur ne dépend d'aucun fournisseur technologique.

## Integration friendly

Les événements et interfaces doivent faciliter l'intégration avec d'autres systèmes.

---

# 43. Non-objectifs initiaux

La première version de PySRMKit ne cherchera pas à fournir :

- une interface Web ;
- un portail fournisseur ;
- une plateforme complète Source-to-Pay ;
- un ERP ;
- un système de facturation ;
- un moteur BPM ;
- un DMS ;
- un système IAM ;
- une plateforme d'analytics ;
- un moteur IA intégré.

Ces fonctionnalités pourront être construites autour du framework.

---

# 44. MVP envisagé

Une première version fonctionnelle pourrait se concentrer sur cinq capacités fondamentales.

```text
PySRMKit MVP
│
├── Supplier Master
│
├── Supplier Lifecycle
│
├── Supplier Onboarding
│
├── Supplier Qualification
└── Supplier Assessments
```

Puis :

```text
Phase 2
├── Compliance
├── Documents
├── Certifications
└── Risk
```

Puis :

```text
Phase 3
├── Performance
├── Scorecards
├── Incidents
├── Segmentation
└── Relationship Management
```

---

# 45. Exemple de parcours complet

```text
Supplier discovered
        │
        ▼
Supplier record created
        │
        ▼
Invitation sent
        │
        ▼
Onboarding started
        │
        ▼
Company information collected
        │
        ▼
Documents collected
        │
        ▼
Compliance checks
        │
        ▼
Risk assessment
        │
        ▼
Qualification review
        │
        ├────────────► REJECTED
        │
        ▼
QUALIFIED
        │
        ▼
ACTIVE
        │
        ▼
Performance monitoring
        │
        ▼
Periodic assessment
        │
        ▼
Risk monitoring
        │
        ├────────────► SUSPENDED
        │
        ▼
Relationship continues
        │
        ▼
OFFBOARDED
```

---

# 46. Vision cible

À terme, PySRMKit doit devenir une **primitive logicielle métier** permettant de construire des systèmes de gestion fournisseur modernes.

Il ne doit pas être pensé comme :

> une copie Python d'Ivalua.

Il doit être pensé comme :

> un modèle métier générique et composable du domaine Supplier Relationship Management.

Sa valeur résidera notamment dans la capacité à standardiser les primitives suivantes :

```text
Supplier
Supplier Identity
Supplier Organization
Supplier Relationship
Supplier Lifecycle
Supplier Onboarding
Supplier Qualification
Supplier Capability
Supplier Document
Supplier Certification
Supplier Compliance
Supplier Risk
Supplier Assessment
Supplier Performance
Supplier Scorecard
Supplier Incident
Supplier Segmentation
Supplier Event
```

Ces primitives devront pouvoir être combinées pour construire des solutions très différentes.

---

# 47. Position dans l'écosystème Py*Kit

```text
                         ENTERPRISE DOMAIN
                               │
        ┌──────────────────────┼────────────────────────┐
        │                      │                        │
        ▼                      ▼                        ▼
   CUSTOMER DOMAIN       SUPPLIER DOMAIN          FINANCE DOMAIN
        │                      │                        │
    PyCRMKit               PySRMKit            PyAccountingKit
                               │
                               ▼
                      PROCUREMENT DOMAIN
                               │
                       PyProcurementKit
                               │
                     ┌─────────┴─────────┐
                     │                   │
                     ▼                   ▼
               PyContractKit        Payments
```

Autour de ces domaines peuvent venir les briques techniques :

```text
PyIAMKit
PyWorkflowKit
PyScheduleKit
PyRuntimeKit
PyTransformKit
PyIngestKit
PyMonitorKit
PyAnalyticsKit
PyAgentsKit
```

---

# 48. Résumé du besoin

PySRMKit doit fournir un **noyau métier open, extensible et indépendant** pour gérer la relation fournisseur.

Le framework devra notamment permettre de :

1. représenter les fournisseurs ;
2. gérer leur identité ;
3. suivre leur cycle de vie ;
4. orchestrer leur onboarding métier ;
5. gérer leur qualification ;
6. référencer leurs documents et certifications ;
7. suivre leur conformité ;
8. mesurer leurs risques ;
9. conduire des évaluations ;
10. mesurer leurs performances ;
11. gérer leurs incidents ;
12. segmenter les fournisseurs ;
13. historiser les décisions ;
14. publier des événements métier ;
15. s'intégrer avec des systèmes Procurement, Accounting, Contract et ERP ;
16. servir de foundation layer à des applications classiques ou agentiques.

La séparation essentielle restera :

```text
PySRMKit
    manages the supplier relationship.

PyProcurementKit
    manages the purchasing process.

PyContractKit
    manages contractual commitments.

PyAccountingKit
    manages financial recognition and settlement.
```

---

# 49. Formulation synthétique

> **PySRMKit is a technology-agnostic Python domain framework for modeling and managing supplier identity, lifecycle, onboarding, qualification, compliance, risk, performance and relationships.**

Ou en français :

> **PySRMKit est un framework métier Python agnostique destiné à modéliser et gérer l'identité, le cycle de vie, l'onboarding, la qualification, la conformité, les risques, la performance et la relation avec les fournisseurs.**

---

# 50. Conclusion

La relation fournisseur constitue un domaine métier suffisamment riche pour justifier une brique autonome.

Le fournisseur ne doit pas être considéré uniquement comme :

```text
Vendor ID + Name + Bank Account
```

mais comme :

```text
Supplier
    +
Identity
    +
Organization
    +
Relationship
    +
Lifecycle
    +
Qualification
    +
Compliance
    +
Risk
    +
Performance
    +
History
```

PySRMKit a vocation à encapsuler cette complexité derrière un modèle cohérent et réutilisable.

Il constituera ainsi le pendant **Supplier Domain** de PyCRMKit et pourra devenir l'une des briques métier fondamentales d'un futur système d'entreprise modulaire et agentique.