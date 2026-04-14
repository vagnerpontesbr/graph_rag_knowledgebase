from __future__ import annotations

import json
from pathlib import Path

ONTOLOGY_TTL = """@prefix : <https://example.org/legal-ontology#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

:LegalOntology a owl:Ontology ;
  rdfs:label "Legal Knowledge Base Ontology (Example)"@en .

:Norm a owl:Class .
:Provision a owl:Class .
:Decision a owl:Class .
:Case a owl:Class .
:Court a owl:Class .
:Topic a owl:Class .

:hasProvision a owl:ObjectProperty .
:applies a owl:ObjectProperty .
:cites a owl:ObjectProperty .
:decidesCase a owl:ObjectProperty .
:aboutTopic a owl:ObjectProperty .
:heardByCourt a owl:ObjectProperty .

:identifier a owl:DatatypeProperty .
:title a owl:DatatypeProperty .
:text a owl:DatatypeProperty .
:decisionDate a owl:DatatypeProperty .
:publishedOn a owl:DatatypeProperty .

:BR a :Jurisdiction ; rdfs:label "Brasil"@pt-BR .
:ResponsabilidadeCivil a :Topic ; rdfs:label "Responsabilidade Civil"@pt-BR .
:DanoMoral a :Topic ; rdfs:label "Dano Moral"@pt-BR ; :broaderTopic :ResponsabilidadeCivil .
"""


def _legal_documents() -> list[dict]:
    return [
        {
            "doc_id": "norm_cc_2002",
            "doc_type": "Norm",
            "title": "Código Civil (Lei 10.406/2002)",
            "text": "Código Civil brasileiro. Base normativa para responsabilidade civil, incluindo dever de reparar danos materiais e morais.",
            "jurisdiction": "BR",
            "topic": "Responsabilidade Civil",
            "published_on": "2002-01-10",
            "source_type": "Lei",
        },
        {
            "doc_id": "prov_cc_art_186",
            "doc_type": "Provision",
            "title": "Art. 186 do Código Civil",
            "text": "Aquele que, por ação ou omissão voluntária, negligência ou imprudência, violar direito e causar dano a outrem comete ato ilícito.",
            "jurisdiction": "BR",
            "topic": "Dano Moral",
            "published_on": "2002-01-10",
            "source_type": "Artigo",
        },
        {
            "doc_id": "prov_cc_art_927",
            "doc_type": "Provision",
            "title": "Art. 927 do Código Civil",
            "text": "Aquele que, por ato ilícito, causar dano a outrem, fica obrigado a repará-lo.",
            "jurisdiction": "BR",
            "topic": "Responsabilidade Civil",
            "published_on": "2002-01-10",
            "source_type": "Artigo",
        },
        {
            "doc_id": "norm_cdc_8078_1990",
            "doc_type": "Norm",
            "title": "Código de Defesa do Consumidor (Lei 8.078/1990)",
            "text": "Dispõe sobre a proteção do consumidor e prevê responsabilidade objetiva por defeito do serviço e do produto.",
            "jurisdiction": "BR",
            "topic": "Direito do Consumidor",
            "published_on": "1990-09-11",
            "source_type": "Lei",
        },
        {
            "doc_id": "prov_cdc_art_14",
            "doc_type": "Provision",
            "title": "Art. 14 do CDC",
            "text": "O fornecedor de serviços responde, independentemente de culpa, pela reparação dos danos causados aos consumidores por defeitos relativos à prestação dos serviços.",
            "jurisdiction": "BR",
            "topic": "Direito do Consumidor",
            "published_on": "1990-09-11",
            "source_type": "Artigo",
        },
        {
            "doc_id": "court_stj",
            "doc_type": "Court",
            "title": "Superior Tribunal de Justiça",
            "text": "Tribunal superior responsável por uniformizar a interpretação da legislação federal no Brasil.",
            "jurisdiction": "BR",
            "topic": "Processo Civil",
            "source_type": "Órgão Julgador",
        },
        {
            "doc_id": "case_resp_123456",
            "doc_type": "Case",
            "title": "REsp 123456",
            "text": "Recurso especial envolvendo pedido de indenização por dano moral e material decorrente de falha na prestação de serviço.",
            "jurisdiction": "BR",
            "topic": "Dano Moral",
            "case_number": "REsp 123456",
            "source_type": "Processo",
        },
        {
            "doc_id": "decision_stj_resp_123456",
            "doc_type": "Decision",
            "title": "Acórdão STJ - REsp 123456",
            "text": "O STJ reconheceu o dever de indenizar, aplicando os arts. 186 e 927 do Código Civil, com análise de nexo causal e extensão do dano moral.",
            "jurisdiction": "BR",
            "topic": "Dano Moral",
            "decision_date": "2024-05-12",
            "source_type": "Acórdão",
        },
        {
            "doc_id": "decision_stj_resp_998877",
            "doc_type": "Decision",
            "title": "Acórdão STJ - REsp 998877",
            "text": "Julgado sobre responsabilidade objetiva em relação de consumo, com fundamento no art. 14 do CDC e precedentes da Corte.",
            "jurisdiction": "BR",
            "topic": "Direito do Consumidor",
            "decision_date": "2023-10-03",
            "source_type": "Acórdão",
        },
        {
            "doc_id": "doctrine_dano_moral_quantum",
            "doc_type": "Doctrine",
            "title": "Doutrina: Fixação do quantum indenizatório em dano moral",
            "text": "A fixação do valor indenizatório deve considerar proporcionalidade, gravidade do dano, capacidade econômica das partes e função pedagógica.",
            "jurisdiction": "BR",
            "topic": "Dano Moral",
            "source_type": "Doutrina",
        },
        {
            "doc_id": "topic_responsabilidade_civil",
            "doc_type": "Topic",
            "title": "Tema: Responsabilidade Civil",
            "text": "Responsabilidade civil trata do dever de reparar danos decorrentes de ato ilícito, culpa, risco da atividade e responsabilidade objetiva em hipóteses legais.",
            "jurisdiction": "BR",
            "topic": "Responsabilidade Civil",
            "source_type": "Taxonomia",
        },
        {
            "doc_id": "topic_dano_moral",
            "doc_type": "Topic",
            "title": "Tema: Dano Moral",
            "text": "Dano moral refere-se à lesão a direitos da personalidade e interesses extrapatrimoniais, sujeitando-se à reparação civil.",
            "jurisdiction": "BR",
            "topic": "Dano Moral",
            "source_type": "Taxonomia",
        },
    ]


def _relations() -> list[dict]:
    return [
        {"source": "norm_cc_2002", "relation": "hasProvision", "target": "prov_cc_art_186"},
        {"source": "norm_cc_2002", "relation": "hasProvision", "target": "prov_cc_art_927"},
        {"source": "norm_cdc_8078_1990", "relation": "hasProvision", "target": "prov_cdc_art_14"},
        {"source": "decision_stj_resp_123456", "relation": "applies", "target": "prov_cc_art_186"},
        {"source": "decision_stj_resp_123456", "relation": "applies", "target": "prov_cc_art_927"},
        {"source": "decision_stj_resp_123456", "relation": "cites", "target": "norm_cc_2002"},
        {"source": "decision_stj_resp_998877", "relation": "applies", "target": "prov_cdc_art_14"},
        {"source": "decision_stj_resp_998877", "relation": "cites", "target": "norm_cdc_8078_1990"},
        {"source": "decision_stj_resp_123456", "relation": "decidesCase", "target": "case_resp_123456"},
        {"source": "case_resp_123456", "relation": "heardByCourt", "target": "court_stj"},
        {"source": "decision_stj_resp_123456", "relation": "aboutTopic", "target": "topic_dano_moral"},
        {"source": "prov_cc_art_186", "relation": "aboutTopic", "target": "topic_dano_moral"},
        {"source": "prov_cc_art_927", "relation": "aboutTopic", "target": "topic_responsabilidade_civil"},
    ]


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def generate_legal_dataset(dataset_path: Path, relations_path: Path, ontology_path: Path) -> tuple[int, int]:
    documents = _legal_documents()
    relations = _relations()

    _write_jsonl(dataset_path, documents)
    _write_jsonl(relations_path, relations)
    ontology_path.parent.mkdir(parents=True, exist_ok=True)
    if not ontology_path.exists():
        ontology_path.write_text(ONTOLOGY_TTL, encoding="utf-8")

    return len(documents), len(relations)


def _legal_documents_en() -> list[dict]:
    return [
        {
            "doc_id": "norm_cc_2002",
            "doc_type": "Norm",
            "title": "Brazilian Civil Code (Law 10.406/2002)",
            "text": "Brazilian Civil Code. Primary normative basis for civil liability, establishing the duty to repair both material and moral damages caused by unlawful acts.",
            "jurisdiction": "BR",
            "topic": "Civil Liability",
            "published_on": "2002-01-10",
            "source_type": "Statute",
        },
        {
            "doc_id": "prov_cc_art_186",
            "doc_type": "Provision",
            "title": "Art. 186 of the Civil Code",
            "text": "Any person who, by voluntary act or omission, negligence, or recklessness, violates a right and causes harm to another person commits an unlawful act.",
            "jurisdiction": "BR",
            "topic": "Moral Damages",
            "published_on": "2002-01-10",
            "source_type": "Article",
        },
        {
            "doc_id": "prov_cc_art_927",
            "doc_type": "Provision",
            "title": "Art. 927 of the Civil Code",
            "text": "Any person who, through an unlawful act, causes harm to another is obliged to repair it.",
            "jurisdiction": "BR",
            "topic": "Civil Liability",
            "published_on": "2002-01-10",
            "source_type": "Article",
        },
        {
            "doc_id": "norm_cdc_8078_1990",
            "doc_type": "Norm",
            "title": "Consumer Protection Code (Law 8.078/1990)",
            "text": "Governs consumer protection in Brazil and establishes strict liability for defective products and services provided by suppliers.",
            "jurisdiction": "BR",
            "topic": "Consumer Law",
            "published_on": "1990-09-11",
            "source_type": "Statute",
        },
        {
            "doc_id": "prov_cdc_art_14",
            "doc_type": "Provision",
            "title": "Art. 14 of the Consumer Protection Code",
            "text": "Service providers are strictly liable, regardless of fault, for damages caused to consumers by defects in the provision of services.",
            "jurisdiction": "BR",
            "topic": "Consumer Law",
            "published_on": "1990-09-11",
            "source_type": "Article",
        },
        {
            "doc_id": "court_stj",
            "doc_type": "Court",
            "title": "Superior Court of Justice (STJ)",
            "text": "The Superior Court of Justice is the highest court responsible for standardising the interpretation of federal legislation in Brazil.",
            "jurisdiction": "BR",
            "topic": "Civil Procedure",
            "source_type": "Adjudicating Body",
        },
        {
            "doc_id": "case_resp_123456",
            "doc_type": "Case",
            "title": "Special Appeal 123456 (REsp 123456)",
            "text": "Special appeal involving a claim for compensation for moral and material damages arising from a failure in service provision.",
            "jurisdiction": "BR",
            "topic": "Moral Damages",
            "case_number": "REsp 123456",
            "source_type": "Court Case",
        },
        {
            "doc_id": "decision_stj_resp_123456",
            "doc_type": "Decision",
            "title": "STJ Ruling — REsp 123456",
            "text": "The STJ upheld the duty to compensate, applying Arts. 186 and 927 of the Civil Code, with analysis of causation and the extent of moral damages.",
            "jurisdiction": "BR",
            "topic": "Moral Damages",
            "decision_date": "2024-05-12",
            "source_type": "Ruling",
        },
        {
            "doc_id": "decision_stj_resp_998877",
            "doc_type": "Decision",
            "title": "STJ Ruling — REsp 998877",
            "text": "Ruling on strict liability in a consumer relationship, grounded in Art. 14 of the Consumer Protection Code and the Court's established precedents.",
            "jurisdiction": "BR",
            "topic": "Consumer Law",
            "decision_date": "2023-10-03",
            "source_type": "Ruling",
        },
        {
            "doc_id": "doctrine_dano_moral_quantum",
            "doc_type": "Doctrine",
            "title": "Doctrine: Calculation of moral damages compensation",
            "text": "The compensation amount for moral damages must consider proportionality, severity of harm, the parties' economic capacity, and the punitive deterrence function.",
            "jurisdiction": "BR",
            "topic": "Moral Damages",
            "source_type": "Legal Doctrine",
        },
        {
            "doc_id": "topic_responsabilidade_civil",
            "doc_type": "Topic",
            "title": "Topic: Civil Liability",
            "text": "Civil liability concerns the duty to repair damages arising from unlawful acts, fault, risk of activity, and strict liability in cases provided for by law.",
            "jurisdiction": "BR",
            "topic": "Civil Liability",
            "source_type": "Taxonomy",
        },
        {
            "doc_id": "topic_dano_moral",
            "doc_type": "Topic",
            "title": "Topic: Moral Damages",
            "text": "Moral damages refer to injury to personality rights and non-patrimonial interests, which are subject to civil compensation under Brazilian law.",
            "jurisdiction": "BR",
            "topic": "Moral Damages",
            "source_type": "Taxonomy",
        },
    ]


def generate_legal_dataset_en(dataset_path: Path, relations_path: Path, ontology_path: Path) -> tuple[int, int]:
    documents = _legal_documents_en()
    relations = _relations()

    _write_jsonl(dataset_path, documents)
    _write_jsonl(relations_path, relations)
    ontology_path.parent.mkdir(parents=True, exist_ok=True)
    if not ontology_path.exists():
        ontology_path.write_text(ONTOLOGY_TTL, encoding="utf-8")

    return len(documents), len(relations)
