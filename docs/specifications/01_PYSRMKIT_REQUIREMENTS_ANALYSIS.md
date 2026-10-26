# PySRMKit — Requirements Analysis

**Document :** `01_PYSRMKIT_REQUIREMENTS_ANALYSIS.md`  
**Projet :** PySRMKit  
**Domaine :** Supplier Relationship Management  
**Type :** Analyse des exigences métier et produit  
**Statut :** Draft initial  
**Version du document :** 0.1.0  
**Document source principal :** `00_PYSRMKIT_EXPRESSION_DU_BESOIN.md`

---

# 1. Objet du document

Ce document transforme l'expression initiale du besoin de PySRMKit en un ensemble structuré :

- d'objectifs produit ;
- de capacités métier ;
- d'exigences fonctionnelles ;
- d'exigences non fonctionnelles ;
- de contraintes ;
- d'invariants attendus ;
- de besoins d'intégration ;
- de critères d'acceptation ;
- de priorités de livraison.

Il ne définit pas encore :

- l'API Python définitive ;
- la topologie exacte des packages ;
- les classes concrètes ;
- les schémas de persistence ;
- les protocoles d'intégration ;
- les choix de bibliothèques ;
- les adapters techniques ;
- les formats d'événements définitifs.

L'objectif est de répondre à la question :

> **Qu'est-ce que PySRMKit doit permettre de représenter, garantir et exposer avant de décider comment l'implémenter ?**

---

# 2. Contexte métier

La relation fournisseur constitue un domaine métier autonome.

Dans de nombreux systèmes d'information, le fournisseur est encore représenté principalement par :

```text
Vendor ID
+
Legal Name
+
Address
+
Tax Identifier
+
Bank Information
+
Contacts
```

Cette représentation ne couvre pas la réalité opérationnelle de la relation fournisseur.

Un fournisseur peut posséder :

- une identité juridique complexe ;
- plusieurs entités ou établissements ;
- plusieurs contacts ;
- plusieurs catégories d'activité ;
- plusieurs capacités ;
- plusieurs relations avec différentes organisations internes ;
- plusieurs qualifications ;
- plusieurs documents ;
- plusieurs certifications ;
- plusieurs risques ;
- plusieurs évaluations ;
- plusieurs incidents ;
- plusieurs métriques de performance ;
- un historique complet de décisions et de changements d'état.

PySRMKit doit donc traiter le fournisseur comme un **agrégat métier riche**.

---

# 3. Problème à résoudre

Le problème principal peut être formulé ainsi :

> Les systèmes d'entreprise disposent rarement d'un modèle fournisseur métier générique, indépendant, réutilisable et suffisamment riche pour représenter le cycle de vie complet de la relation fournisseur.

Les informations fournisseur sont souvent dispersées entre :

```text
ERP
Procurement
Accounting
Contract Management
Document Management
Risk Platforms
Compliance Tools
Emails
Spreadsheets
Workflows
Data Platforms
```

Cette fragmentation entraîne notamment :

- duplication des données ;
- divergences de référentiels ;
- dépendance à des plateformes propriétaires ;
- difficulté à historiser les décisions ;
- difficulté à réutiliser les règles métier ;
- onboarding difficile à piloter ;
- qualification peu explicite ;
- conformité difficile à consolider ;
- gestion des risques fragmentée ;
- performance fournisseur isolée des autres dimensions ;
- intégrations point-à-point ;
- faible composabilité des capacités métier.

---

# 4. Vision produit

PySRMKit doit devenir :

> **un framework métier Python agnostique permettant de modéliser et gérer la relation fournisseur indépendamment des technologies d'exécution, de persistence, d'interface et d'intégration.**

Le framework doit être utilisable comme noyau métier par :

```text
Supplier Portal
ERP
Procurement Platform
Source-to-Pay Platform
Supplier Risk Platform
Vendor Management System
Contract Management Platform
Marketplace B2B
Microservice
Agent
Agentic Enterprise Platform
CLI
Batch
Notebook
API
```

PySRMKit n'est pas une application SRM complète.

Il constitue :

```text
Domain Model
+
Business Rules
+
Lifecycle
+
Policies
+
Use Cases
+
Domain Events
+
Ports
```

---

# 5. Objectifs produit

## 5.1 Objectif principal

Fournir un noyau métier réutilisable capable de représenter le fournisseur et sa relation avec une organisation pendant l'ensemble de son cycle de vie.

## 5.2 Objectifs secondaires

PySRMKit doit permettre de :

1. centraliser un modèle fournisseur canonique ;
2. représenter son identité métier ;
3. représenter ses structures organisationnelles ;
4. gérer ses contacts et ses implantations ;
5. gérer ses catégories et capacités ;
6. gérer son onboarding ;
7. gérer sa qualification ;
8. représenter ses documents et certifications ;
9. suivre sa conformité ;
10. suivre ses risques ;
11. conduire des évaluations ;
12. enregistrer sa performance ;
13. construire des scorecards ;
14. enregistrer les incidents ;
15. gérer sa segmentation ;
16. représenter ses relations commerciales ;
17. historiser son évolution ;
18. publier des événements métier ;
19. permettre l'extension des règles métier ;
20. faciliter l'intégration avec l'écosystème d'entreprise.

---

# 6. Non-objectifs

PySRMKit ne doit pas devenir directement :

- un ERP ;
- un portail fournisseur ;
- une plateforme Source-to-Pay ;
- un moteur de sourcing ;
- un moteur RFQ/RFP ;
- un système de Purchase Orders ;
- un système de Purchase Requisitions ;
- un moteur de facturation ;
- un système Accounts Payable ;
- un moteur comptable ;
- un moteur de paiement ;
- un système complet de Contract Lifecycle Management ;
- un système IAM ;
- un moteur BPM générique ;
- un DMS ;
- un moteur de notifications ;
- un moteur de reporting BI ;
- un orchestrateur technique ;
- un moteur IA intégré.

Ces fonctions peuvent consommer ou compléter PySRMKit.

---

# 7. Frontières du domaine

## 7.1 Domaine couvert

Le cœur de PySRMKit couvre :

```text
Supplier Identity
Supplier Organization
Supplier Lifecycle
Supplier Contacts
Supplier Locations
Supplier Categories
Supplier Capabilities
Supplier Onboarding
Supplier Qualification
Supplier Documents
Supplier Certifications
Supplier Compliance
Supplier Risk
Supplier Assessments
Supplier Performance
Supplier Scorecards
Supplier Incidents
Supplier Segmentation
Supplier Relationships
Supplier Status
Supplier Events
Supplier History
```

## 7.2 Domaine explicitement adjacent

Les domaines suivants interagissent avec PySRMKit sans lui appartenir :

```text
Procurement
Accounting
Contracts
Payments
IAM
Workflow
Scheduling
Runtime
Documents
Notifications
Analytics
Data Integration
Agents
```

## 7.3 Règle de frontière

La règle fondamentale est :

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

# 8. Acteurs et parties prenantes

PySRMKit étant un framework métier, les acteurs ne correspondent pas uniquement à des utilisateurs humains.

## 8.1 Acteurs humains potentiels

- Supplier Manager ;
- Procurement Manager ;
- Buyer ;
- Compliance Officer ;
- Risk Manager ;
- Legal Reviewer ;
- Finance Reviewer ;
- Supplier Quality Manager ;
- Business Owner ;
- Supplier Contact ;
- Auditor ;
- Administrator.

## 8.2 Systèmes acteurs

- ERP ;
- Procurement Platform ;
- Contract Management System ;
- Accounting Platform ;
- Risk Platform ;
- Compliance Provider ;
- Document Management System ;
- Company Registry ;
- Tax Validation Service ;
- Sanctions Screening Service ;
- Bank Verification Service ;
- Data Platform ;
- Event Bus ;
- Agentic Platform.

## 8.3 Agents logiciels

Un agent pourra notamment :

- rechercher des fournisseurs éligibles ;
- identifier des documents expirés ;
- analyser des changements de risque ;
- préparer une revue ;
- comparer des performances ;
- déclencher ou préparer un onboarding ;
- proposer une suspension ;
- expliquer une non-qualification.

Cependant :

> **un agent ne doit jamais contourner les invariants métier du domaine.**

---

# 9. Capabilities métier

Les capabilities constituent la vue fonctionnelle principale du produit.

```text
PySRMKit
│
├── Supplier Master
├── Supplier Organization
├── Lifecycle Management
├── Onboarding
├── Qualification
├── Documents
├── Certifications
├── Compliance
├── Risk
├── Assessments
├── Performance
├── Scorecards
├── Incidents
├── Segmentation
├── Relationships
├── History & Audit
├── Domain Events
└── Integration Ports
```

---

# 10. CAP-01 — Supplier Master

## 10.1 Intention

Permettre de représenter un fournisseur indépendamment des systèmes externes qui le référencent.

## 10.2 Exigences

Le framework doit pouvoir représenter :

- un identifiant interne ;
- un code fournisseur ;
- une raison sociale ;
- un nom commercial ;
- un type de fournisseur ;
- un statut ;
- une étape de lifecycle ;
- des identifiants externes ;
- des catégories ;
- des contacts ;
- des implantations ;
- des métadonnées extensibles.

## 10.3 Identifiants externes

Le modèle doit permettre de référencer notamment :

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

Ces identifiants ne doivent pas constituer l'identité métier fondamentale du fournisseur.

## 10.4 Critères d'acceptation

- un fournisseur peut exister sans ERP Vendor ID ;
- plusieurs identifiants externes peuvent être associés au même fournisseur ;
- un identifiant externe doit pouvoir être typé ;
- la suppression ou modification d'un identifiant externe ne doit pas changer l'identité intrinsèque du fournisseur.

---

# 11. CAP-02 — Supplier Organization

## 11.1 Intention

Représenter la structure organisationnelle d'un fournisseur.

## 11.2 Structures attendues

Le domaine doit pouvoir exprimer :

- maison mère ;
- filiale ;
- établissement ;
- branche ;
- groupe ;
- organisation liée.

## 11.3 Exigences

Le framework doit permettre :

- de relier plusieurs entités fournisseur ;
- de représenter une hiérarchie ;
- de distinguer groupe et entité juridique ;
- de conserver des relations non hiérarchiques ;
- de rattacher des relations commerciales à une entité précise.

---

# 12. CAP-03 — Supplier Contacts

Le domaine doit permettre de représenter plusieurs contacts pour un fournisseur.

Types de contacts possibles :

- commercial ;
- direction ;
- comptabilité ;
- support ;
- conformité ;
- juridique ;
- responsable de compte.

Le modèle doit permettre au minimum de représenter :

- l'identité du contact ;
- son rôle ;
- son périmètre ;
- ses moyens de communication ;
- son statut actif/inactif ;
- son rattachement organisationnel.

---

# 13. CAP-04 — Supplier Locations

Le domaine doit permettre de représenter plusieurs implantations :

- siège ;
- usine ;
- agence ;
- entrepôt ;
- bureau ;
- centre logistique.

Une implantation doit pouvoir être reliée :

- au fournisseur ;
- à une entité organisationnelle ;
- à un pays ;
- à une zone géographique ;
- à une fonction opérationnelle.

Le modèle d'adresse doit rester extensible et multi-pays.

---

# 14. CAP-05 — Categories & Capabilities

## 14.1 Supplier Categories

Le domaine doit pouvoir classifier les fournisseurs par catégories.

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

## 14.2 Supplier Capabilities

Le domaine doit pouvoir représenter les capacités réelles ou déclarées d'un fournisseur.

Exemple :

```text
Supplier
├── Cloud Consulting
├── Python Development
├── Data Engineering
└── Managed Services
```

## 14.3 Distinction structurante

```text
Category
    = classification métier

Capability
    = capacité à fournir un produit, service ou savoir-faire
```

---

# 15. CAP-06 — Supplier Lifecycle

Le lifecycle constitue une capability centrale.

## 15.1 États de référence

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

## 15.2 Exigences fonctionnelles

Le framework doit :

- connaître l'état courant ;
- contrôler les transitions autorisées ;
- refuser les transitions invalides ;
- enregistrer la cause d'une transition lorsque nécessaire ;
- publier un événement métier lorsque la transition est significative ;
- permettre l'extension ou la configuration de certaines transitions ;
- permettre la reconstruction de l'historique.

## 15.3 Invariant

> Un changement d'état ne doit pas être une simple modification arbitraire d'un champ `status`.

---

# 16. CAP-07 — Supplier Onboarding

## 16.1 Parcours conceptuel

```text
Invitation
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

## 16.2 Exigences

PySRMKit doit pouvoir représenter :

- l'état de l'onboarding ;
- les étapes métier ;
- les informations attendues ;
- les éléments fournis ;
- les éléments manquants ;
- les décisions ;
- les rejets ;
- les validations ;
- la complétude ;
- la progression métier.

## 16.3 Contrainte

PySRMKit ne doit pas imposer :

- le moteur BPM ;
- l'ordre technique d'exécution ;
- les notifications ;
- la gestion des tâches humaines ;
- le scheduling.

Le framework définit **ce qui est valide métier**, pas **comment l'entreprise orchestre le travail**.

---

# 17. CAP-08 — Supplier Qualification

## 17.1 Intention

Établir si un fournisseur est autorisé à intervenir dans un périmètre donné.

## 17.2 Dimensions potentielles

La qualification peut dépendre de :

- catégorie ;
- pays ;
- organisation ;
- business unit ;
- type de prestation ;
- seuil financier ;
- niveau de risque.

## 17.3 Exigences

Le framework doit permettre :

- plusieurs qualifications pour un même fournisseur ;
- plusieurs périmètres ;
- plusieurs états de qualification ;
- une date d'effet ;
- une date éventuelle d'expiration ;
- une justification ;
- des preuves ;
- la réévaluation ;
- le rejet ;
- le retrait de qualification.

## 17.4 Exemple

```text
ACME Consulting

IT Consulting       QUALIFIED
Cloud Services      QUALIFIED
Cybersecurity       PENDING
Construction        NOT_QUALIFIED
```

## 17.5 Invariant

> `Supplier == ACTIVE` ne signifie pas automatiquement `Supplier == QUALIFIED for everything`.

---

# 18. CAP-09 — Supplier Documents

## 18.1 Documents concernés

Exemples :

- extrait d'immatriculation ;
- attestation fiscale ;
- attestation sociale ;
- assurance ;
- RIB ;
- licences ;
- documents réglementaires ;
- politique ESG ;
- preuves de conformité.

## 18.2 Modèle attendu

Le domaine doit pouvoir représenter :

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

## 18.3 Contraintes

PySRMKit :

- peut référencer un document ;
- peut suivre sa validité ;
- peut suivre son statut de vérification ;
- peut publier des événements associés.

PySRMKit ne doit pas obligatoirement :

- stocker le fichier ;
- gérer les blobs ;
- gérer les permissions documentaires ;
- fournir un DMS.

---

# 19. CAP-10 — Supplier Certifications

Le domaine doit représenter notamment :

```text
ISO 9001
ISO 27001
ISO 14001
SOC 2
EcoVadis
Professional Licenses
```

Une certification doit pouvoir porter :

- une autorité émettrice ;
- une date d'émission ;
- une date d'expiration ;
- un périmètre ;
- un statut ;
- une preuve documentaire.

Le framework doit permettre de détecter conceptuellement :

- certification valide ;
- certification expirante ;
- certification expirée ;
- certification révoquée ;
- certification non vérifiée.

---

# 20. CAP-11 — Supplier Compliance

Le domaine doit permettre de représenter différentes obligations :

- juridique ;
- fiscale ;
- sanctions ;
- KYS ;
- obligations sociales ;
- ESG ;
- cybersécurité ;
- protection des données ;
- assurance professionnelle.

## 20.1 Exigences

Le framework doit pouvoir représenter :

- le type de contrôle ;
- son statut ;
- sa date ;
- sa portée ;
- ses preuves ;
- son résultat ;
- son niveau de sévérité ;
- sa source ;
- sa prochaine revue éventuelle.

## 20.2 Contrainte

Le domaine ne doit pas dépendre d'un fournisseur externe spécifique de compliance.

---

# 21. CAP-12 — Supplier Risk

## 21.1 Taxonomie initiale

```text
Supplier Risk
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

## 21.2 Exigences

Un fournisseur doit pouvoir posséder :

- plusieurs risques ;
- plusieurs évaluations d'un même risque ;
- un niveau courant ;
- un historique ;
- une date d'évaluation ;
- une source ;
- une justification ;
- des mesures de mitigation.

## 21.3 Exigence temporelle

Le risque doit être considéré comme une donnée évolutive.

```text
Risk(t1) != Risk(t2)
```

Le framework doit préserver cette dimension temporelle.

---

# 22. CAP-13 — Supplier Assessments

Le framework doit permettre plusieurs types d'évaluations :

- questionnaire ;
- audit ;
- évaluation métier ;
- revue conformité ;
- revue annuelle ;
- revue risque ;
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

Le moteur doit permettre de séparer :

```text
Assessment Definition
Assessment Execution
Assessment Responses
Assessment Scoring
Assessment Decision
```

sans nécessairement imposer leur implémentation dès la première version.

---

# 23. CAP-14 — Supplier Performance

Le domaine doit permettre de suivre des métriques telles que :

- Delivery Performance ;
- Quality ;
- Service Level ;
- Cost ;
- Responsiveness ;
- Innovation ;
- Compliance ;
- Sustainability ;
- Incident Rate.

## 23.1 Exigences

Une mesure de performance doit pouvoir être :

- datée ;
- contextualisée ;
- associée à une période ;
- associée à un périmètre ;
- sourcée ;
- agrégée.

---

# 24. CAP-15 — Supplier Scorecards

Le framework doit pouvoir construire une vue agrégée de plusieurs métriques.

Exemple :

```text
Quality        91/100
Delivery       86/100
Cost           78/100
Compliance    100/100
ESG            83/100
---------------------
Overall         87/100
```

Les règles de pondération doivent être :

- explicites ;
- extensibles ;
- remplaçables ;
- non figées dans le noyau.

---

# 25. CAP-16 — Supplier Incidents

Le domaine doit pouvoir enregistrer notamment :

- retard ;
- non-conformité ;
- problème qualité ;
- violation contractuelle ;
- incident sécurité ;
- fraude ;
- interruption de service ;
- non-conformité réglementaire.

Un incident doit pouvoir influencer :
- la performance ;
- le risque ;
- la qualification ;
- le statut ;
- la segmentation.

Ces effets doivent cependant passer par des règles métier explicites et non par des effets de bord implicites.

---

# 26. CAP-17 — Supplier Segmentation

Segments de référence :

```text
Strategic
Critical
Preferred
Approved
Standard
Transactional
Restricted
```

La segmentation peut dépendre de :

- volume d'achat ;
- criticité ;
- dépendance ;
- risque ;
- performance ;
- substituabilité.

La logique de segmentation doit être encapsulable dans une politique extensible.

---

# 27. CAP-18 — Supplier Relationships

## 27.1 Intention

Distinguer :

```text
Who the supplier is
```

de :

```text
How our organization works with the supplier
```

## 27.2 Exemple

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

## 27.3 Exigence structurante

Une même entité fournisseur doit pouvoir entretenir plusieurs relations distinctes avec différentes entités internes.

---

# 28. CAP-19 — Multi-organisation

PySRMKit doit supporter des groupes complexes :

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

Le même fournisseur peut donc avoir :

- des statuts différents ;
- des qualifications différentes ;
- des risques différents ;
- des documents requis différents ;
- des relations différentes ;

selon l'organisation considérée.

---

# 29. CAP-20 — Multi-pays

Le framework doit être extensible sur :

- identifiants légaux ;
- identifiants fiscaux ;
- formats d'adresse ;
- obligations réglementaires ;
- documents ;
- devises ;
- langues.

PySRMKit ne doit pas considérer le modèle français comme modèle universel.

---

# 30. CAP-21 — History & Temporal Model

Le framework doit permettre de reconstruire une chronologie métier telle que :

```text
Supplier Created
Onboarding Started
Documents Submitted
Compliance Approved
Supplier Qualified
Supplier Activated
Performance Reviewed
Risk Increased
Supplier Suspended
Supplier Reactivated
Supplier Offboarded
```

## 30.1 Exigences

Pour les changements significatifs, il doit être possible de retrouver :

- le changement ;
- la date ;
- l'état précédent ;
- l'état suivant ;
- la cause ;
- les preuves ;
- l'initiateur lorsque disponible.

---

# 31. CAP-22 — Auditability

Les décisions critiques doivent pouvoir répondre à :

```text
WHAT happened?
WHO initiated it?
WHEN?
WHY?
FROM which state?
TO which state?
WITH which evidence?
```

Cette exigence concerne particulièrement :

- onboarding ;
- qualification ;
- conformité ;
- suspension ;
- blocage ;
- réactivation ;
- modification d'informations sensibles.

---

# 32. CAP-23 — Domain Events

Les changements significatifs doivent pouvoir produire des événements métier.

Événements envisagés :

```text
SupplierCreated
SupplierRegistered
SupplierInvited
SupplierOnboardingStarted
SupplierInformationUpdated
SupplierDocumentSubmitted
SupplierDocumentExpired
SupplierQualificationRequested
SupplierQualified
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

## 32.1 Exigences

Un événement doit pouvoir transporter au minimum :

- son type ;
- son identifiant ;
- son horodatage ;
- l'identifiant du fournisseur ;
- la donnée métier pertinente ;
- des métadonnées de corrélation si disponibles.

La structure exacte sera définie ultérieurement.

---

# 33. CAP-24 — Policies

Les règles variables selon les organisations ne doivent pas être codées comme des règles universelles.

Politiques envisagées :

```text
RiskPolicy
QualificationPolicy
ActivationPolicy
SegmentationPolicy
CompliancePolicy
PerformancePolicy
```

## 33.1 Exigence

Le noyau doit fournir :

- des abstractions stables ;
- des comportements par défaut lorsque pertinents ;
- des points d'extension ;
- la possibilité de remplacer une politique.

Exemple conceptuel :

```python
qualification_policy.evaluate(supplier)
```

---

# 34. CAP-25 — Integration Ports

Les systèmes externes doivent être accessibles via des ports.

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

## 34.1 Exigence

Le domaine ne doit pas importer directement :

- un SDK Ivalua ;
- un SDK SAP ;
- un client AWS ;
- un client Azure ;
- Kafka ;
- PostgreSQL ;
- un framework Web.

Ces dépendances doivent rester hors du cœur métier.

---

# 35. Exigences fonctionnelles consolidées

## FR-001 — Créer un fournisseur

Le système doit permettre de créer une entité fournisseur avec une identité minimale valide.

## FR-002 — Enrichir l'identité fournisseur

Le système doit permettre d'ajouter ou modifier les attributs métier autorisés du fournisseur.

## FR-003 — Gérer les identifiants

Le système doit supporter plusieurs identifiants internes et externes typés.

## FR-004 — Gérer les organisations fournisseur

Le système doit supporter les relations groupe, filiale, établissement et entité liée.

## FR-005 — Gérer les contacts

Le système doit supporter plusieurs contacts et rôles.

## FR-006 — Gérer les implantations

Le système doit supporter plusieurs sites et adresses.

## FR-007 — Gérer les catégories

Le système doit permettre l'association d'un fournisseur à plusieurs catégories.

## FR-008 — Gérer les capacités

Le système doit pouvoir exprimer les capacités d'un fournisseur.

## FR-009 — Gérer le lifecycle

Le système doit appliquer une machine à états contrôlée.

## FR-010 — Démarrer un onboarding

Le système doit pouvoir représenter le démarrage d'un onboarding.

## FR-011 — Suivre un onboarding

Le système doit suivre son état et sa complétude métier.

## FR-012 — Qualifier un fournisseur

Le système doit pouvoir créer une qualification contextualisée.

## FR-013 — Rejeter une qualification

Le système doit pouvoir enregistrer un rejet et sa justification.

## FR-014 — Révoquer une qualification

Le système doit pouvoir retirer une qualification existante.

## FR-015 — Référencer un document

Le système doit pouvoir enregistrer les métadonnées d'un document.

## FR-016 — Suivre l'expiration documentaire

Le système doit pouvoir déterminer l'état temporel d'un document.

## FR-017 — Gérer les certifications

Le système doit supporter émission, expiration, révocation et vérification.

## FR-018 — Enregistrer un contrôle de conformité

Le système doit pouvoir conserver le résultat d'un contrôle.

## FR-019 — Enregistrer un risque

Le système doit pouvoir enregistrer un risque typé et contextualisé.

## FR-020 — Réévaluer un risque

Le système doit préserver l'historique des changements.

## FR-021 — Créer une évaluation

Le système doit pouvoir créer différents types d'assessment.

## FR-022 — Compléter une évaluation

Le système doit pouvoir enregistrer réponses, scores, preuves et décision.

## FR-023 — Enregistrer une performance

Le système doit pouvoir enregistrer une métrique datée.

## FR-024 — Construire une scorecard

Le système doit permettre l'agrégation de métriques.

## FR-025 — Enregistrer un incident

Le système doit pouvoir enregistrer un incident fournisseur.

## FR-026 — Segmenter un fournisseur

Le système doit permettre l'application d'une politique de segmentation.

## FR-027 — Suspendre un fournisseur

Le système doit contrôler la transition vers `SUSPENDED`.

## FR-028 — Bloquer un fournisseur

Le système doit contrôler la transition vers `BLOCKED`.

## FR-029 — Réactiver un fournisseur

Le système doit contrôler les conditions de réactivation.

## FR-030 — Offboarder un fournisseur

Le système doit représenter la fin de la relation.

## FR-031 — Historiser les décisions

Le système doit conserver les éléments nécessaires à la traçabilité.

## FR-032 — Publier des domain events

Le système doit produire des événements pour les changements métier significatifs.

## FR-033 — Supporter plusieurs relations

Un fournisseur doit pouvoir être lié à plusieurs organisations internes.

## FR-034 — Supporter plusieurs pays

Le modèle doit rester extensible à différents cadres nationaux.

## FR-035 — Exposer des ports

Le domaine doit pouvoir interagir avec les systèmes externes via des abstractions.

---

# 36. Exigences non fonctionnelles

## NFR-001 — Technology Agnostic

Le cœur ne doit imposer :

- aucun ORM ;
- aucune base de données ;
- aucun framework Web ;
- aucun cloud ;
- aucun système de message ;
- aucun moteur de workflow ;
- aucun système IAM ;
- aucun DMS.

## NFR-002 — Persistence Agnostic

Le domaine doit pouvoir être utilisé avec :

```text
PostgreSQL
MySQL
SQLite
MongoDB
DynamoDB
Snowflake
In-memory
```

sans dépendance directe vers ces technologies.

## NFR-003 — Composability

Les capabilities doivent pouvoir être utilisées indépendamment lorsque cela est cohérent.

Exemple :

- utiliser Supplier Master + Qualification sans Performance ;
- utiliser Supplier Master + Risk sans Onboarding complet ;
- utiliser Assessments sans DMS intégré.

## NFR-004 — Extensibility

Les organisations doivent pouvoir remplacer les politiques métier variables.

## NFR-005 — Explicitness

Les règles critiques doivent être représentées explicitement.

À éviter :

```text
hidden side effects
magic status changes
implicit coupling
framework-specific behavior
```

## NFR-006 — Auditability

Les décisions critiques doivent être explicables a posteriori.

## NFR-007 — Deterministic Business Rules

Pour un même état métier et les mêmes entrées, une règle pure doit produire le même résultat, sauf lorsqu'une dépendance externe ou temporelle explicitement injectée intervient.

## NFR-008 — Testability

Le domaine doit pouvoir être testé sans :

- base de données ;
- réseau ;
- broker ;
- cloud ;
- framework Web.

## NFR-009 — Serialization Friendly

Les objets métier pertinents doivent pouvoir être transformés vers des représentations sérialisables sans dépendre d'un protocole de transport particulier.

## NFR-010 — Integration Friendly

Les événements et ports doivent permettre l'intégration sans couplage direct.

## NFR-011 — Multi-organization

Le modèle doit pouvoir représenter des règles et relations différentes selon l'entité interne.

## NFR-012 — Multi-country

Le domaine ne doit pas encoder les règles françaises comme règles universelles.

## NFR-013 — Maintainability

Le framework doit favoriser :

- séparation des responsabilités ;
- faible couplage ;
- forte cohésion ;
- vocabulaire métier explicite ;
- architecture lisible.

## NFR-014 — Backward Compatibility

Une fois les primitives publiques stabilisées, les évolutions doivent limiter les ruptures non nécessaires.

## NFR-015 — Agent Compatibility

Le framework doit pouvoir être utilisé depuis un système agentique sans rendre les agents responsables des invariants métier.

---

# 37. Contraintes architecturales

Les exigences induisent les contraintes suivantes.

## AC-001 — Domain-first

Le domaine doit être indépendant des couches techniques.

## AC-002 — No ORM in Core

Aucune entité métier ne doit dépendre directement d'un ORM.

## AC-003 — No HTTP in Core

Le cœur ne définit pas la couche HTTP.

## AC-004 — No Workflow Engine in Core

PySRMKit contrôle les transitions métier mais ne devient pas un moteur BPM.

## AC-005 — No Physical Document Storage in Core

Le domaine référence les documents mais n'impose pas leur stockage.

## AC-006 — External Systems Behind Ports

Les intégrations externes doivent être abstraites.

## AC-007 — Events Are Domain Concepts

Les domain events doivent exister indépendamment de Kafka, RabbitMQ, SNS ou autre bus.

## AC-008 — Configurability Without Losing Invariants

Les organisations peuvent personnaliser les politiques, mais ne doivent pas pouvoir contourner les invariants fondamentaux du modèle.

---

# 38. Invariants métier candidats

Ces invariants devront être confirmés et raffinés dans un document dédié.

## INV-001

Un fournisseur possède une identité métier stable indépendante d'un ERP Vendor ID.

## INV-002

Une transition de lifecycle invalide doit être rejetée.

## INV-003

Un fournisseur ne peut pas être considéré comme qualifié globalement uniquement parce qu'il est actif.

## INV-004

Une qualification doit toujours avoir un périmètre.

## INV-005

Un contrôle de conformité doit conserver son résultat et son contexte.

## INV-006

Une mesure de risque doit être datée.

## INV-007

Une mesure de performance doit être datée ou rattachée à une période.

## INV-008

Un document expiré ne doit pas être considéré comme valide.

## INV-009

Une certification révoquée ne doit pas être considérée comme active.

## INV-010

Une suspension ou un blocage doit être justifiable.

## INV-011

Une réactivation ne doit pas supprimer l'historique de suspension.

## INV-012

Un offboarding ne doit pas effacer l'historique de la relation.

## INV-013

Les événements métier doivent refléter une transition réellement acceptée par le domaine.

---

# 39. Cas d'utilisation prioritaires

## UC-001 — Register Supplier

Créer un fournisseur et lui attribuer son identité métier.

## UC-002 — Invite Supplier

Passer un fournisseur dans un état permettant de commencer l'onboarding.

## UC-003 — Start Onboarding

Initialiser l'état métier d'onboarding.

## UC-004 — Complete Supplier Information

Compléter les informations requises.

## UC-005 — Submit Supplier Document

Référencer une pièce justificative.

## UC-006 — Evaluate Compliance

Enregistrer un contrôle de conformité.

## UC-007 — Request Qualification

Demander une qualification pour un périmètre.

## UC-008 — Approve Qualification

Valider la qualification.

## UC-009 — Activate Supplier

Activer un fournisseur lorsque les préconditions métier sont remplies.

## UC-010 — Register Risk

Enregistrer une évaluation de risque.

## UC-011 — Complete Assessment

Finaliser une évaluation.

## UC-012 — Record Performance

Enregistrer une mesure de performance.

## UC-013 — Report Incident

Enregistrer un incident.

## UC-014 — Suspend Supplier

Suspendre temporairement une relation.

## UC-015 — Reactivate Supplier

Réactiver un fournisseur lorsque les conditions sont réunies.

## UC-016 — Offboard Supplier

Clore la relation fournisseur.

---

# 40. Interactions avec les autres Py*Kit

## 40.1 PyProcurementKit

```text
PySRMKit
    WHO can we buy from?

PyProcurementKit
    WHAT do we want to buy?
    HOW do we buy it?
```

PyProcurementKit peut consommer :

- fournisseurs actifs ;
- fournisseurs qualifiés ;
- catégories ;
- capacités ;
- statut de risque ;
- statut de conformité.

## 40.2 PyAccountingKit

PyAccountingKit peut créer ou maintenir une représentation comptable à partir d'un fournisseur.

```text
Supplier
    │
    ▼
Vendor Account
    │
    ▼
Accounts Payable
```

Invariant conceptuel :

```text
Supplier != Vendor Ledger Account
```

## 40.3 PyContractKit

PyContractKit gère les engagements contractuels.

PySRMKit peut :

- référencer l'existence de contrats ;
- utiliser des informations contractuelles comme contexte ;

mais ne doit pas absorber le domaine contractuel.

## 40.4 PyCRMKit

Les deux frameworks constituent deux faces relationnelles :

```text
Customer Domain  → PyCRMKit
Supplier Domain  → PySRMKit
```

## 40.5 PyWorkflowKit

PySRMKit définit :

```text
Supplier can be qualified.
```

PyWorkflowKit peut définir :

```text
who approves
in what order
with which SLA
with which escalation
```

## 40.6 PyRuntimeKit

PyRuntimeKit peut exécuter des workloads utilisant PySRMKit mais ne doit pas modifier les règles métier.

## 40.7 PyAgentsKit / Synqentra

Les agents peuvent piloter des cas d'usage applicatifs, mais :

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

# 41. Modèle d'intégration cible

Architecture conceptuelle :

```text
┌──────────────────────────────────────────────────────┐
│                    Applications                      │
│ Portal │ ERP │ Procurement │ API │ Agents │ CLI     │
└────────────────────────┬─────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────┐
│                 Application Layer                    │
│ Commands │ Queries │ Use Cases │ Policies           │
└────────────────────────┬─────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────┐
│                      PySRMKit                        │
│ Supplier │ Lifecycle │ Qualification │ Risk │ ...   │
└────────────────────────┬─────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────┐
│                        Ports                         │
│ Repositories │ Registry │ Risk │ Documents │ Events │
└────────────────────────┬─────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────┐
│                      Adapters                        │
│ PostgreSQL │ SAP │ Ivalua │ Kafka │ S3 │ REST ...  │
└──────────────────────────────────────────────────────┘
```

---

# 42. Priorisation MoSCoW

## MUST

Pour une première version réellement exploitable :

- Supplier Master ;
- Supplier identity ;
- identifiers ;
- contacts ;
- locations ;
- categories ;
- lifecycle ;
- onboarding state ;
- qualification ;
- assessments de base ;
- domain events ;
- history minimal ;
- ports de persistence ;
- technology agnosticism.

## SHOULD

- documents ;
- certifications ;
- compliance ;
- risk ;
- configurable policies ;
- multi-organization ;
- audit enrichi.

## COULD

- performance ;
- scorecards ;
- incidents ;
- segmentation ;
- relationship modeling avancé ;
- multi-country rule packs ;
- projection models.

## WON'T — initialement

- portail Web ;
- BPM ;
- DMS ;
- IAM ;
- BI ;
- AI engine ;
- sourcing ;
- purchase orders ;
- invoicing ;
- payment engine.

---

# 43. Proposition de découpage MVP

## Phase 1 — Supplier Core

```text
Supplier Master
Identity
Identifiers
Contacts
Locations
Categories
Capabilities
Lifecycle
Domain Events
History
```

## Phase 2 — Onboarding & Qualification

```text
Onboarding
Qualification
Assessments
Policies
```

## Phase 3 — Trust & Control

```text
Documents
Certifications
Compliance
Risk
```

## Phase 4 — Relationship Intelligence

```text
Performance
Scorecards
Incidents
Segmentation
Relationships
```

---

# 44. Critères d'acceptation du MVP

Le MVP pourra être considéré comme fonctionnel lorsque les scénarios suivants pourront être exécutés sans dépendance à une infrastructure externe.

## Scenario A — Supplier creation

```text
Create Supplier
→ Add identifiers
→ Add contact
→ Add location
→ Add category
```

Résultat attendu :

- l'objet fournisseur est valide ;
- aucune base de données n'est requise ;
- l'identité reste indépendante des systèmes externes.

## Scenario B — Lifecycle

```text
PROSPECTIVE
→ INVITED
→ ONBOARDING
→ UNDER_REVIEW
→ QUALIFIED
→ ACTIVE
```

Résultat attendu :

- chaque transition valide est acceptée ;
- une transition interdite est rejetée ;
- les événements associés sont produits.

## Scenario C — Qualification

```text
Supplier
→ Qualification requested for IT_SERVICES
→ Reviewed
→ QUALIFIED
```

Résultat attendu :

- la qualification reste contextualisée ;- elle ne qualifie pas automatiquement le fournisseur sur d'autres catégories.

## Scenario D — Audit

Après plusieurs transitions, il doit être possible de reconstruire :

```text
what
when
why
from
to
```

## Scenario E — Technology independence

La suite de tests métier doit s'exécuter :

```text
without database
without network
without cloud
without web framework
without message broker
```

---

# 45. Risques produit

## RISK-001 — Sur-modélisation

Le domaine SRM est très vaste.

Risque :

> vouloir représenter dès la première version toutes les subtilités d'Ivalua, Coupa, SAP Ariba ou Jaggaer.

Réponse :

- partir des primitives métier ;
- garder les extensions hors du noyau ;
- avancer par capabilities.

## RISK-002 — Couplage avec Procurement

Supplier Management et Procurement sont fortement liés.

Risque :

> faire dériver PySRMKit vers un framework Source-to-Pay.

Réponse :

maintenir la frontière :

```text
SRM = supplier relationship
Procurement = purchasing process
```

## RISK-003 — Confusion Supplier / Vendor Account

Le modèle comptable ne doit pas devenir le modèle fournisseur.

## RISK-004 — Lifecycle trop rigide

Une machine à états universelle pourrait ne pas convenir à toutes les organisations.

Réponse :

- noyau standard ;
- extensions contrôlées ;
- invariants non contournables.

## RISK-005 — Generic Framework Syndrome

Un framework trop générique peut devenir abstrait au point de perdre sa valeur métier.

Réponse :

- conserver un vocabulaire SRM concret ;
- fournir des primitives métier opinionated ;
- permettre l'extension aux frontières.

## RISK-006 — Couplage aux agents

L'intégration agentique ne doit pas faire de PySRMKit un framework d'agents.

---

# 46. Questions ouvertes

Les questions suivantes devront être tranchées dans les documents suivants.

## Q-001

`Supplier` et `SupplierOrganization` doivent-ils être deux agrégats distincts ?

## Q-002

`SupplierRelationship` doit-il être un agrégat de premier niveau ?

## Q-003

Le lifecycle est-il global au fournisseur ou spécifique à une relation avec une organisation interne ?

## Q-004

La qualification appartient-elle :

- au Supplier ;
- à SupplierRelationship ;
- à un contexte organisation + catégorie ?

## Q-005

Les documents appartiennent-ils au Supplier, à une Legal Entity, à une Relationship ou à plusieurs scopes ?

## Q-006

La conformité est-elle modélisée comme :

- check ;
- requirement ;
- assessment ;
- decision ;
- combinaison de ces concepts ?

## Q-007

Faut-il distinguer :

```text
Risk Definition
Risk Assessment
Risk Observation
Risk Decision
```

## Q-008

Le modèle d'historisation doit-il être :

- state + audit records ;
- event sourcing ;
- compatible avec les deux ?

## Q-009

Les policies sont-elles synchrones uniquement dans le cœur ?

## Q-010

Quels objets doivent être immuables ?

---

# 47. Décisions à reporter

Les points suivants ne doivent pas être figés à ce stade :

- dataclasses vs attrs vs Pydantic ;
- UUID vs autre identifiant ;
- sync vs async repositories ;
- event sourcing ou non ;
- SQLAlchemy adapter ;
- Mongo adapter ;
- Kafka adapter ;
- FastAPI integration ;
- package layout ;
- naming exact des modules ;
- protocoles d'intégration ;
- mécanisme de plugin ;
- configuration de policies ;
- formats de sérialisation.

Ces décisions appartiennent à la conception technique, pas à l'analyse du besoin.

---

# 48. Indicateurs de qualité du produit

PySRMKit sera considéré comme bien conçu si :

1. le domaine peut être utilisé sans infrastructure ;
2. les concepts SRM sont reconnaissables dans l'API ;
3. les règles critiques sont explicites ;
4. les transitions invalides sont impossibles ou rejetées ;
5. les technologies externes restent remplaçables ;
6. les politiques organisationnelles sont extensibles ;
7. le framework peut être intégré à plusieurs types d'applications ;
8. les décisions métier sont auditables ;
9. les objets supportent les contextes multi-organisation et multi-pays ;
10. les agents peuvent utiliser le domaine sans pouvoir contourner ses invariants.

---

# 49. Matrice capability / priorité

| Capability | Priorité | MVP | Phase |
|---|---:|---:|---:|
| Supplier Master | MUST | Oui | 1 |
| Supplier Organization | MUST | Oui | 1 |
| Contacts | MUST | Oui | 1 |
| Locations | MUST | Oui | 1 |
| Categories | MUST | Oui | 1 |
| Capabilities | MUST | Oui | 1 |
| Lifecycle | MUST | Oui | 1 |
| Domain Events | MUST | Oui | 1 |
| History | MUST | Oui | 1 |
| Onboarding | MUST | Oui | 2 |
| Qualification | MUST | Oui | 2 |
| Assessments | MUST | Oui | 2 |
| Policies | SHOULD | Oui | 2 |
| Documents | SHOULD | Non | 3 |
| Certifications | SHOULD | Non | 3 |
| Compliance | SHOULD | Non | 3 |
| Risk | SHOULD | Non | 3 |
| Performance | COULD | Non | 4 |
| Scorecards | COULD | Non | 4 |
| Incidents | COULD | Non | 4 |
| Segmentation | COULD | Non | 4 |
| Relationships avancées | COULD | Non | 4 |

---

# 50. Requirements Traceability — vue initiale

```text
Business Need
    │
    ▼
Capability
    │
    ▼
Functional Requirement
    │
    ▼
Business Rule / Invariant
    │
    ▼
Use Case
    │
    ▼
Acceptance Scenario
    │
    ▼
Implementation
```

Cette chaîne devra être conservée dans la documentation future afin d'éviter :

- les fonctionnalités sans besoin métier ;
- les règles sans justification ;
- les classes créées uniquement par mimétisme technique.

---

# 51. Synthèse

PySRMKit doit fournir un **Supplier Domain Engine** générique, riche et composable.

Son cœur fonctionnel se concentre sur :

```text
Identity
+
Organization
+
Lifecycle
+
Onboarding
+
Qualification
+
Trust
+
Risk
+
Assessment
+
Performance
+
Relationship
+
History
```

Son cœur architectural se concentre sur :

```text
Domain-first
+
Explicit business rules
+
State machines
+
Policies
+
Ports
+
Domain events
+
Auditability
+
Technology independence
```

La distinction structurante est :

```text
Supplier
    ≠
ERP Vendor Record

Supplier
    ≠
Vendor Ledger Account

Supplier Relationship Management
    ≠
Procurement

PySRMKit
    ≠
Source-to-Pay Platform
```

---

# 52. Conclusion

L'analyse confirme que PySRMKit correspond à un domaine suffisamment riche et autonome pour justifier une bibliothèque métier dédiée.

Le framework doit fournir un modèle fournisseur canonique qui puisse devenir la source de vérité métier ou, selon l'architecture adoptée, la couche de normalisation de plusieurs systèmes.

La priorité n'est pas de reproduire les écrans ou workflows d'une plateforme SRM existante.

La priorité est de formaliser les primitives fondamentales du Supplier Domain :

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

Le document suivant devra transformer cette analyse en une vision produit et des principes d'architecture plus précis :

> **`02_PYSRMKIT_PRODUCT_VISION_AND_ARCHITECTURE_PRINCIPLES.md`**

Il devra notamment établir :

- les principes de conception ;
- les bounded contexts ou sous-domaines internes ;
- le positionnement DDD ;
- les règles de dépendance ;
- les principes de composabilité ;
- les principes de stabilité de l'API ;
- la frontière entre domain layer, application layer, ports et adapters.