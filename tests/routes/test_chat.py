import asyncio
import random
import string
from typing import Iterable, List

import pytest
from adi_rag_utils.audit.models import LLMModel, MessageFeedbackType
from adi_rag_utils.common.models import ChatType, RoleType
from loguru import logger
from starlette import status
from starlette.testclient import TestClient

from app.core.config import settings
from app.domain.chat_router.workflows.apfs.schema import APFSFilterMetadata
from app.domain.chat_router.workflows.data_sources.opensearch.schema import (
    Aggregation,
    SearchResponse,
)
from app.domain.embeddings.schema import VectorDBResult
from app.domain.llm_chat.schema import (
    AskLLMQuestionRequestSchema,
    ChatOptionV2,
    CreateChatSchemaV2,
    GenerateAggregationSchema,
)
from app.domain.llm_feedback.schema import (
    MessageFeedbackCreateSchema,
    MessageFeedbackUpdateSchema,
)
from app.domain.query_mutation.rewriter.schema import GeneralSubqueryMetadata
from app.domain.retrieval.schema import Domain, TavilySearchResult


def create_new_chat(client):
    chat = client.post(
        url="/api/v1/chat",
        data=CreateChatSchemaV2(
            options=ChatOptionV2(
                model=LLMModel.GPT4, search_filters=["DOCUMENT_GENERAL"]
            ),
            description="Explain Issues in china",
        ).model_dump_json(),
    )
    chat_id = chat.json()["id"]
    return chat_id


def create_apfs_chat(client):
    chat = client.post(
        url="/api/v1/chat",
        data=CreateChatSchemaV2(
            options=ChatOptionV2(
                model=LLMModel.CLAUDE3SONNET,
                search_filters=["DOCUMENT_APFS"],
                chat_type=ChatType.APFS,
            ),
            description="Explain Issues in china",
        ).model_dump_json(),
    )
    chat_id = chat.json()["id"]
    return chat_id


async def async_generate_random_string(length: int = 10):
    """Generate a random string of uppercase and lowercase letters with the given length asynchronously."""
    letters = string.ascii_letters
    for i in range(length):
        await asyncio.sleep(
            0.1
        )  # simulate async I/O, e.g. 'await' on a real I/O operation
        yield "".join(random.choice(letters) for _ in range(length))


def gpt_4_payload() -> dict:
    return {
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant. Use Markdown for references in the format answer part1[Title1](Download Link1) answer part2[Title2](Download Link2). Each source has the following components Title: Title 1; Content: Content 1; Download Link: download_link; text: text Answer using markdown to provide references example: In-network deductibles are $500 for employee and $1000 for family [Title 1](Download Link 1), Overlake is in-network for the employee plan [Title 2](Download Link 2), etc..",
            },
            {
                "role": "user",
                "content": "What are the most pressing health-related concerns in Indonesia? Always provide the actual download link in references with titles",
            },
        ],
        "chat_options": {"source": "all", "model": "gpt-4"},
    }


def ask_question_payload() -> dict:
    return {
        "content": "What are the most pressing health-related concerns in Indonesia? Always provide the actual download link in references with titles",
    }


def generate_random_strings(num_strings: int = 5, string_length: int = 20) -> Iterable:
    output = []
    for _ in range(num_strings):
        random_string = "".join(
            random.choice(string.ascii_letters) for _ in range(string_length)
        )
        output.append(random_string)

    return iter(output)


def get_search_results() -> List[VectorDBResult]:
    search_results = [
        {
            "doc_id": "abc12354",
            "isbn": "",
            "title": "Second Decentralized Health Services",
            "people": [],
            "series": "",
            "source": "Reports and Recommendations of the President",
            "authors": [],
            "sectors": ["Health"],
            "combined": "Title: Second Decentralized Health Services; Country: Indonesia; Sector: Health; Content: 2. \nFrom 1970 to 2001, life expectancy at birth increased from 46 to 64 years of age for \nmales and to 68 years of age for females, reflecting the decline in the infant and under-5 \nmortality rates. Infant mortality declined from 145 to 33 infant deaths and under-5 mortality \ndeclined from 172 to 45 per thousand live births. Easier access to health services combined \nwith economic growth and better education contributed to improving the health status. However, \nIndonesia’s health status indicators remain low2 and achievements have been uneven across \nprovinces, between urban and rural areas, and between rich and poor segments of the \npopulation. With 25% of all under-5-year-old children underweight and 50% of pregnant women \nsuffering from iron deficiency anemia, malnutrition remains a public health issue. Maternal \nmortality, estimated at 380 maternal deaths per 100,000 live births, is unacceptably high. While \ncardiovascular and chronic diseases have become the main causes of mortality, infectious and \nparasitic diseases, which particularly affect the poor, dominate morbidity. Tuberculosis, malaria, \nrespiratory infections, and diarrhea remain major public health issues. This combination of \nchronic, life-style, and infectious diseases creates a double burden of diseases for the health \nsystem of the country. A detailed description of the health sector and its performance in the \nproject area is in Appendix 2. \n \n3. \nOver the last 3 decades, Indonesia has given priority to improving physical access to \nprimary health care (PHC) services. The average distance to a health facility in 2002 was 5 \nkilometers in rural areas and 1.5 kilometers in urban areas, but chronic underfunding and \ninefficient targeting has prevented better results. Total national expenditures for health have \nbeen low by international standards. In 1995, only 1.6% of gross domestic product was spent on \nhealth. The proportion increased to 2.7% in 2000, but the Government’s share of health \nexpenditure, excluding external aid, fell from 46.0% in 1995 to 23.7%. The percentage of central \nGovernment expenditure allocated to the health sector is only 2%, compared with 5% in the \nPhilippines and 8% in Thailand. Health expenditure per capita ($19) is below the average of \nlow-income countries ($21), the Philippines ($33), and Thailand ($71). Chronic underfunding \nhas affected maintenance of facilities; procurement of medical equipment, drugs, and other \nsupplies; and the quality of training for health workers, before and after graduation. A low 30% \nutilization rate of public health services suggests low client satisfaction.  \n \n4. \nConsultations in the villages during project preparation confirmed that low quality and \ninadequate services that do not respond to needs felt by the local population were important \nreasons for low utilization of public health services. For the poor, even minimal user fees can be \nan obstacle to the use of health services. The World Bank found that the richest 20% of the \n",
            "keywords": ["rrp", " ino", " health services", " adb"],
            "countries": ["Indonesia"],
            "sub_regions": [],
            "content_date": "2003-11-30",
            "doc_language": "en",
            "project_link": "abc123",
            "data_uploaded": "2014-09-29",
            "download_link": "/sites/default/files/project-documents//helloworld.pdf",
            "project_numbers": ["99999-999"],
            "research_topics": [],
        }
    ]

    return [VectorDBResult(**result) for result in search_results]


def get_tavily_search_results() -> List[TavilySearchResult]:
    tavily_result = TavilySearchResult(
        title="Economic Forecasts | Asian Development Bank",
        url="https://www.adb.org/what-we-do/economic-forecasts/editions",
        content="However, consumption and investment are forecast to boost aggregate regional growth to 4.8% in 2023, as earlier forecast, with the projection for 2024 revised down only marginally to 4.7%.\u200b\nAsian Development Outlook (ADO) April 2023\nGrowth in developing Asia is forecast at 4.8% this year and in 2024, up from 4.2% last year. Supplement: Recovery Faces Diverse Challenges\nThis Supplement revises the growth forecasts for developing Asia from 5.2% to 4.6% for 2022 and from 5.3% to 5.2% for 2023, reflecting worsened economic prospects because of COVID-19 lockdowns in the People’s Republic of China, more aggressive monetary tightening in advanced economies, and fallout from Russia’s protracted invasion of Ukraine.\n Asian Development Outlook (ADO) 2021 Supplement: Renewed Outbreaks and Divergent Recoveries\nADB is adjusting its 2021 growth outlook for developing Asia as renewed COVID-19 outbreaks, new virus variants, and an uneven vaccine rollout slow the recovery in some economies in the region.\n What Drives Innovation in Asia?\nGrowth in the region is expected to slow sharply to 2.2% in 2020 under the effects of the current health emergency and then rebound to 6.2% in 2021.\n Economic activity in Developing Asia is forecast to contract by 0.4% this year, and then expand by up to 6.8% in 2021 as the region moves toward recovery from the effects of the coronavirus disease (COVID-19) pandemic.\n",
    )

    return [tavily_result]


def init_llm_clients(mocker) -> None:
    mocker.patch(
        "app.domain.retrieval.retrievers.pgvector.AsyncPGVectorV2.__init__",
        lambda self, *args, **kwargs: None,
    )
    mocker.patch(
        "app.domain.llm_client.service.GPTClient.__init__",
        lambda self, *args, **kwargs: None,
    )
    mocker.patch(
        "app.domain.llm_client.service.Claude3SonnetClient.__init__",
        lambda self, *args, **kwargs: None,
    )


def rag_search_ask_question(
    mocker,
    is_async: bool = True,
    use_gpt: bool = False,
    use_claude3: bool = False,
):
    mocker.patch(
        "app.domain.retrieval.retrievers.pgvector.RAGRetrievalService.search",
        return_value=get_search_results(),
    )

    mocker.patch(
        "app.domain.retrieval.service.RetrievalService.get_llm_prompt",
        return_value=("some sysprompt", "some prompt"),
    )

    if use_gpt:
        mocker.patch(
            "app.domain.llm_client.service.GPTClient.send_message",
            return_value=(
                async_generate_random_string()
                if is_async
                else generate_random_strings()
            ),
        )

    if use_claude3:
        mocker.patch(
            "app.domain.llm_client.service.Claude3SonnetClient.send_message",
            return_value=(
                async_generate_random_string()
                if is_async
                else generate_random_strings()
            ),
        )


def create_multi_chat(
    client: TestClient,
) -> int:
    chat_id = create_new_chat(client)
    client.put(url=f"/api/v1/chat/{chat_id}", json=ask_question_payload())

    create_chat_schema_1 = CreateChatSchemaV2(
        options=ChatOptionV2(model=LLMModel.GPT4, search_filters=["DOCUMENT_GENERAL"]),
        parent_chat_id=chat_id,
        description="Explain Issues in china",
    )
    child_chat_1 = client.post(
        url="/api/v1/chat", data=create_chat_schema_1.model_dump_json()
    )
    child_chat_1_id = child_chat_1.json()["id"]
    client.put(url=f"/api/v1/chat/{child_chat_1_id}", json=ask_question_payload())

    return chat_id


@pytest.mark.anyio
async def test_ask_question(client: TestClient, mocker):
    init_llm_clients(mocker)

    rag_search_ask_question(mocker, use_gpt=True)

    resp = client.put(url="/api/v1/chat/1", json=ask_question_payload())

    for data in resp.stream:
        logger.success(data)

    assert resp.status_code == status.HTTP_200_OK


@pytest.mark.anyio
async def test_ask_question_gpt4_no_access(client: TestClient, mocker):
    init_llm_clients(mocker)

    rag_search_ask_question(mocker, use_gpt=True)

    resp = client.put(url="/api/v1/chat/2", json=ask_question_payload())

    for data in resp.stream:
        logger.success(data)

    assert resp.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.anyio
async def test_ask_question_gpt4(client: TestClient, mocker):
    init_llm_clients(mocker)

    rag_search_ask_question(mocker, use_gpt=True)

    chat_id = create_new_chat(client)
    resp = client.put(url=f"/api/v1/chat/{chat_id}", json=ask_question_payload())
    assert resp.status_code == status.HTTP_200_OK

    for data in resp.stream:
        logger.success(data)


@pytest.mark.anyio
async def test_ask_question_gpt4_hybrid(client: TestClient, mocker):
    init_llm_clients(mocker)

    rag_search_ask_question(mocker, use_gpt=True)
    chat_id = create_new_chat(client)
    resp = client.put(url=f"/api/v1/chat/{chat_id}", json=ask_question_payload())
    assert resp.status_code == status.HTTP_200_OK

    for data in resp.stream:
        logger.success(data)


@pytest.mark.anyio
async def test_create_chat(client: TestClient, mocker):
    init_llm_clients(mocker)
    create_chat_schema = CreateChatSchemaV2(
        options=ChatOptionV2(model=LLMModel.GPT4, search_filters=["DOCUMENT_GENERAL"]),
        description="Explain Issues in china",
    )
    resp = client.post(url="/api/v1/chat", data=create_chat_schema.model_dump_json())

    assert resp.status_code == status.HTTP_201_CREATED


@pytest.mark.anyio
async def test_create_pdf_chat_wrong_model(client: TestClient, mocker):
    init_llm_clients(mocker)

    create_chat_schema = CreateChatSchemaV2(
        options=ChatOptionV2(
            model=LLMModel.GPT4,
            search_filters=[],
            uploaded_files=["s3://some-file/pdf.txt"],
        ),
        description="Explain Issues in china",
    )
    resp = client.post(url="/api/v1/chat", data=create_chat_schema.model_dump_json())

    assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.anyio
async def test_create_chat_with_invalid_parent_chat_id(client: TestClient, mocker):
    init_llm_clients(mocker)
    create_chat_schema = CreateChatSchemaV2(
        options=ChatOptionV2(model=LLMModel.GPT4, search_filters=["DOCUMENT_GENERAL"]),
        parent_chat_id=99,
        description="Explain Issues in china",
    )
    resp = client.post(url="/api/v1/chat", data=create_chat_schema.model_dump_json())

    assert resp.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.anyio
async def test_create_chat_with_search_filters(client: TestClient, mocker):
    init_llm_clients(mocker)
    create_chat_schema = CreateChatSchemaV2(
        options=ChatOptionV2(model=LLMModel.GPT4, search_filters=["DOCUMENT_GENERAL"]),
        description="Explain Issues in china",
    )
    resp = client.post(url="/api/v1/chat", data=create_chat_schema.model_dump_json())

    assert resp.status_code == status.HTTP_201_CREATED


@pytest.mark.anyio
async def test_ask_question_gpt4_hybrid_with_search_filters(client: TestClient, mocker):
    init_llm_clients(mocker)

    rag_search_ask_question(mocker, use_gpt=True)
    chat_id = create_new_chat(client)
    resp = client.put(url=f"/api/v1/chat/{chat_id}", json=ask_question_payload())
    assert resp.status_code == status.HTTP_200_OK

    for data in resp.stream:
        logger.success(data)


@pytest.mark.anyio
async def test_list_chats_by_user(client: TestClient, mocker):
    init_llm_clients(mocker)
    resp = client.get(url="/api/v1/chat/user/list")

    assert resp.status_code == status.HTTP_200_OK


@pytest.mark.anyio
async def test_get_chat_history(client: TestClient, mocker):
    init_llm_clients(mocker)
    resp = client.get(url="/api/v1/chat/1/history")

    assert resp.status_code == status.HTTP_200_OK


@pytest.mark.anyio
async def test_get_chat_questions_from_chat_history(client: TestClient, mocker):
    init_llm_clients(mocker)
    resp = client.get(url="/api/v1/chat/1/questions")

    assert resp.status_code == status.HTTP_200_OK


@pytest.mark.anyio
async def test_get_chat_history_that_user_has_no_access(client: TestClient, mocker):
    init_llm_clients(mocker)
    resp = client.get(url="/api/v1/chat/2/history")

    assert resp.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.anyio
async def test_get_chat_history_that_does_not_exist(client: TestClient, mocker):
    init_llm_clients(mocker)
    resp = client.get(url="/api/v1/chat/9999/history")

    assert resp.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.anyio
async def test_regenerate_latest_answer_by_chat_id(client: TestClient, mocker):
    init_llm_clients(mocker)
    rag_search_ask_question(mocker, use_gpt=True)

    resp = client.post(url="/api/v1/chat/1/regenerate")
    chat_history = client.get(url="/api/v1/chat/1/history")

    assert resp.status_code == status.HTTP_200_OK
    assert chat_history.json()["history"][0]["regenerated_messages"]


@pytest.mark.anyio
async def test_post_message_feedback_by_message_id(client: TestClient, mocker):
    init_llm_clients(mocker)
    rag_search_ask_question(mocker, use_gpt=True)

    resp = client.post(
        url="/api/v1/chat/1/message/16/feedback",
        data=MessageFeedbackCreateSchema(
            feedback_type=MessageFeedbackType.THUMBS_DOWN,
            feedback_comment="This answer sucks!",
        ).model_dump_json(),
    )

    assert resp.status_code == status.HTTP_201_CREATED


@pytest.mark.anyio
async def test_post_message_feedback_by_message_id_409(client: TestClient, mocker):
    init_llm_clients(mocker)
    rag_search_ask_question(mocker, use_gpt=True)

    resp = client.post(
        url="/api/v1/chat/1/message/16/feedback",
        data=MessageFeedbackCreateSchema(
            feedback_type=MessageFeedbackType.THUMBS_DOWN,
            feedback_comment="This answer sucks!",
        ).model_dump_json(),
    )

    assert resp.status_code == status.HTTP_409_CONFLICT


@pytest.mark.anyio
async def test_post_message_feedback_by_message_id_404(client: TestClient, mocker):
    init_llm_clients(mocker)
    rag_search_ask_question(mocker, use_gpt=True)

    resp = client.post(
        url="/api/v1/chat/10/message/19/feedback",
        data=MessageFeedbackCreateSchema(
            feedback_type=MessageFeedbackType.THUMBS_DOWN,
            feedback_comment="This answer sucks!",
        ).model_dump_json(),
    )

    assert resp.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.anyio
async def test_get_message_feedback_by_message_id(client: TestClient, mocker):
    init_llm_clients(mocker)
    rag_search_ask_question(mocker, use_gpt=True)

    resp = client.get(url="/api/v1/chat/1/message/16/feedback")

    assert resp.status_code == status.HTTP_200_OK


@pytest.mark.anyio
async def test_update_message_feedback_comment_by_message_id(
    client: TestClient, mocker
):
    init_llm_clients(mocker)
    rag_search_ask_question(mocker, use_gpt=True)

    resp = client.put(
        url="/api/v1/chat/1/message/16/feedback",
        data=MessageFeedbackUpdateSchema(
            feedback_type=MessageFeedbackType.THUMBS_DOWN,
            feedback_comment="This answer sucks alot!",
        ).model_dump_json(),
    )

    assert resp.status_code == status.HTTP_200_OK


@pytest.mark.anyio
async def test_delete_message_feedback_by_message_id(client: TestClient, mocker):
    init_llm_clients(mocker)
    rag_search_ask_question(mocker, use_gpt=True)

    resp = client.delete(url="/api/v1/chat/1/message/16/feedback")

    assert resp.status_code == status.HTTP_200_OK


@pytest.mark.anyio
async def test_get_message_feedback_by_chat_id(client: TestClient, mocker):
    init_llm_clients(mocker)
    rag_search_ask_question(mocker, use_gpt=True)

    resp = client.get(url="/api/v1/chat/1/feedback/list")

    assert resp.status_code == status.HTTP_200_OK


@pytest.mark.anyio
async def test_get_chat_by_id(client: TestClient, mocker):
    init_llm_clients(mocker)
    rag_search_ask_question(mocker, use_gpt=True)

    chat_id = 1

    resp = client.get(url=f"/api/v1/chat/{chat_id}")

    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["id"] == chat_id


@pytest.mark.anyio
async def test_list_llm_clients(client: TestClient, mocker):
    init_llm_clients(mocker)
    rag_search_ask_question(mocker, use_gpt=True)

    resp = client.get(url="/api/v1/chat/llm")

    assert resp.status_code == status.HTTP_200_OK


@pytest.mark.anyio
async def test_regenerate_on_empty_chat_should_return_400(client: TestClient, mocker):
    init_llm_clients(mocker)
    rag_search_ask_question(mocker, use_gpt=True)

    create_chat_schema = CreateChatSchemaV2(
        options=ChatOptionV2(model=LLMModel.GPT4, search_filters=["DOCUMENT_GENERAL"]),
        description="Explain Issues in china",
    )
    resp = client.post(url="/api/v1/chat", data=create_chat_schema.model_dump_json())

    assert resp.status_code == status.HTTP_201_CREATED

    new_chat_id = resp.json()["id"]
    resp = client.post(url=f"/api/v1/chat/{new_chat_id}/regenerate")

    assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.anyio
async def test_summarise_chat_single_chat(client: TestClient, mocker):
    init_llm_clients(mocker)
    rag_search_ask_question(mocker, use_gpt=True)
    mocker.patch(
        "app.domain.llm_client.service.Claude3SonnetClient.send_message",
        return_value=async_generate_random_string(),
    )

    resp = client.post(
        url="/api/v1/chat/1/summarise",
        data=GenerateAggregationSchema(model=LLMModel.GPT4).model_dump_json(),
    )

    assert resp.status_code == status.HTTP_201_CREATED


@pytest.mark.anyio
async def test_summarise_no_history(client: TestClient, mocker):
    init_llm_clients(mocker)
    rag_search_ask_question(mocker, use_gpt=True, use_claude3=True)

    create_chat_schema_1 = CreateChatSchemaV2(
        options=ChatOptionV2(
            model=LLMModel.CLAUDE3SONNET,
            search_filters=["DOCUMENT_GENERAL"],
        ),
        description="Explain Issues in china",
        parent_chat_id=1,
    )
    client.post(url="/api/v1/chat", data=create_chat_schema_1.model_dump_json())

    create_chat_schema_2 = CreateChatSchemaV2(
        options=ChatOptionV2(model=LLMModel.GPT4, search_filters=["DOCUMENT_GENERAL"]),
        parent_chat_id=1,
        description="Explain Issues in china",
    )
    client.post(url="/api/v1/chat", data=create_chat_schema_2.model_dump_json())

    resp = client.post(
        url="/api/v1/chat/1/summarise",
        data=GenerateAggregationSchema(model=LLMModel.CLAUDE3SONNET).model_dump_json(),
    )

    assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.anyio
async def test_summarise_multi_chat(client: TestClient, mocker):
    init_llm_clients(mocker)
    rag_search_ask_question(mocker, use_gpt=True, use_claude3=True)

    chat_id = create_multi_chat(client)

    resp = client.post(
        url=f"/api/v1/chat/{chat_id}/summarise",
        data=GenerateAggregationSchema(model=LLMModel.GPT4).model_dump_json(),
    )

    assert resp.status_code == status.HTTP_201_CREATED

    for data in resp.stream:
        logger.success(data)


@pytest.mark.anyio
async def test_summarise_twice(client: TestClient, mocker):
    init_llm_clients(mocker)
    rag_search_ask_question(mocker, use_gpt=True, use_claude3=True)

    settings.ENABLE_V2_SUMMARISATION_FEATURE = False

    chat_id = create_multi_chat(client)

    resp = client.post(
        url=f"/api/v1/chat/{chat_id}/summarise",
        data=GenerateAggregationSchema(model=LLMModel.GPT4).model_dump_json(),
    )

    assert resp.status_code == status.HTTP_201_CREATED

    resp_2 = client.post(
        url=f"/api/v1/chat/{chat_id}/summarise",
        data=GenerateAggregationSchema(model=LLMModel.GPT4).model_dump_json(),
    )

    assert resp_2.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.anyio
async def test_ask_question_after_summary(client: TestClient, mocker):
    init_llm_clients(mocker)
    rag_search_ask_question(mocker, use_gpt=True, use_claude3=True)

    settings.ENABLE_V2_SUMMARISATION_FEATURE = False

    chat_id = create_multi_chat(client)

    resp = client.post(
        url=f"/api/v1/chat/{chat_id}/summarise",
        data=GenerateAggregationSchema(model=LLMModel.GPT4).model_dump_json(),
    )

    assert resp.status_code == status.HTTP_201_CREATED

    resp_2 = client.put(url=f"/api/v1/chat/{chat_id}", json=ask_question_payload())

    assert resp_2.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.anyio
async def test_summarise_v2(client: TestClient, mocker):
    init_llm_clients(mocker)
    rag_search_ask_question(mocker, use_gpt=True, use_claude3=True)

    settings.ENABLE_V2_SUMMARISATION_FEATURE = True

    chat_id = create_multi_chat(client)

    resp = client.post(
        url=f"/api/v1/chat/{chat_id}/summarise",
        data=GenerateAggregationSchema(model=LLMModel.GPT4).model_dump_json(),
    )

    assert resp.status_code == status.HTTP_201_CREATED

    client.put(url=f"/api/v1/chat/{chat_id}", json=ask_question_payload())

    resp_2 = client.post(
        url=f"/api/v1/chat/{chat_id}/summarise",
        data=GenerateAggregationSchema(model=LLMModel.GPT4).model_dump_json(),
    )

    assert resp_2.status_code == status.HTTP_201_CREATED


@pytest.mark.anyio
async def test_summarise_regenerate(client: TestClient, mocker):
    init_llm_clients(mocker)
    rag_search_ask_question(mocker, use_gpt=True, use_claude3=True)

    settings.ENABLE_V2_SUMMARISATION_FEATURE = True

    chat_id = create_multi_chat(client)

    resp = client.post(
        url=f"/api/v1/chat/{chat_id}/summarise",
        data=GenerateAggregationSchema(model=LLMModel.GPT4).model_dump_json(),
    )

    assert resp.status_code == status.HTTP_201_CREATED

    resp_2 = client.post(url=f"/api/v1/chat/{chat_id}/summarise/regenerate")

    assert resp_2.status_code == status.HTTP_201_CREATED


@pytest.mark.anyio
async def test_summarise_invalid_chat(client: TestClient, mocker):
    init_llm_clients(mocker)
    rag_search_ask_question(mocker, use_gpt=True, use_claude3=True)

    resp = client.post(
        url="/api/v1/chat/999/summarise",
        data=GenerateAggregationSchema(model=LLMModel.GPT4).model_dump_json(),
    )

    assert resp.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.anyio
async def test_get_summary_invalid_chat(client: TestClient, mocker):
    init_llm_clients(mocker)
    rag_search_ask_question(mocker, use_gpt=True, use_claude3=True)

    resp = client.get(
        url="/api/v1/chat/999/summarise",
    )

    assert resp.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.anyio
async def test_get_summary(client: TestClient, mocker):
    init_llm_clients(mocker)
    rag_search_ask_question(mocker, use_gpt=True, use_claude3=True)

    chat_id = create_multi_chat(client)

    client.post(
        url=f"/api/v1/chat/{chat_id}/summarise",
        data=GenerateAggregationSchema(model=LLMModel.GPT4).model_dump_json(),
    )

    resp = client.get(
        url=f"/api/v1/chat/{chat_id}/summarise",
    )

    assert resp.status_code == status.HTTP_200_OK


@pytest.mark.anyio
async def test_combine_chat_single_chat(client: TestClient, mocker):
    init_llm_clients(mocker)
    rag_search_ask_question(mocker, use_gpt=True)
    chat_id = create_new_chat(client)

    resp = client.post(
        url=f"/api/v1/chat/{chat_id}/combine",
        data=GenerateAggregationSchema(model=LLMModel.CLAUDE3SONNET).model_dump_json(),
    )

    assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.anyio
async def test_combine_no_history(client: TestClient, mocker):
    init_llm_clients(mocker)
    rag_search_ask_question(mocker, use_gpt=True, use_claude3=True)

    resp = client.post(
        url="/api/v1/chat/1/combine",
        data=GenerateAggregationSchema(model=LLMModel.CLAUDE3SONNET).model_dump_json(),
    )

    assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.anyio
async def test_combine_multi_chat(client: TestClient, mocker):
    init_llm_clients(mocker)
    rag_search_ask_question(mocker, use_gpt=True, use_claude3=True)

    chat_id = create_multi_chat(client)

    resp = client.post(
        url=f"/api/v1/chat/{chat_id}/combine",
        data=GenerateAggregationSchema(model=LLMModel.GPT4).model_dump_json(),
    )

    assert resp.status_code == status.HTTP_201_CREATED

    for data in resp.stream:
        logger.success(data)


@pytest.mark.anyio
async def test_combine_twice(client: TestClient, mocker):
    init_llm_clients(mocker)
    rag_search_ask_question(mocker, use_gpt=True, use_claude3=True)

    chat_id = create_multi_chat(client)

    resp = client.post(
        url=f"/api/v1/chat/{chat_id}/combine",
        data=GenerateAggregationSchema(model=LLMModel.GPT4).model_dump_json(),
    )

    assert resp.status_code == status.HTTP_201_CREATED

    resp_2 = client.post(
        url=f"/api/v1/chat/{chat_id}/combine",
        data=GenerateAggregationSchema(model=LLMModel.GPT4).model_dump_json(),
    )

    assert resp_2.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.anyio
async def test_ask_question_after_combination(client: TestClient, mocker):
    init_llm_clients(mocker)
    rag_search_ask_question(mocker, use_gpt=True, use_claude3=True)

    chat_id = create_multi_chat(client)

    resp = client.post(
        url=f"/api/v1/chat/{chat_id}/combine",
        data=GenerateAggregationSchema(model=LLMModel.GPT4).model_dump_json(),
    )

    assert resp.status_code == status.HTTP_201_CREATED

    resp_2 = client.put(url=f"/api/v1/chat/{chat_id}", json=ask_question_payload())

    assert resp_2.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.anyio
async def test_combine_invalid_chat(client: TestClient, mocker):
    init_llm_clients(mocker)
    rag_search_ask_question(mocker, use_gpt=True, use_claude3=True)

    resp = client.post(
        url="/api/v1/chat/999/combine",
        data=GenerateAggregationSchema(model=LLMModel.GPT4).model_dump_json(),
    )

    assert resp.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.anyio
async def test_get_combination_invalid_chat(client: TestClient, mocker):
    init_llm_clients(mocker)
    rag_search_ask_question(mocker, use_gpt=True, use_claude3=True)

    resp = client.get(
        url="/api/v1/chat/999/combine",
    )

    assert resp.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.anyio
async def test_get_combination(client: TestClient, mocker):
    init_llm_clients(mocker)
    rag_search_ask_question(mocker, use_gpt=True, use_claude3=True)

    chat_id = create_multi_chat(client)

    client.post(
        url=f"/api/v1/chat/{chat_id}/combine",
        data=GenerateAggregationSchema(model=LLMModel.GPT4).model_dump_json(),
    )

    resp = client.get(
        url=f"/api/v1/chat/{chat_id}/combine",
    )

    assert resp.status_code == status.HTTP_200_OK


@pytest.mark.anyio
async def test_get_message_retrieval_prompt(client: TestClient, mocker):
    init_llm_clients(mocker)
    rag_search_ask_question(mocker, use_gpt=True, use_claude3=True)

    chat_id = 1
    message_id = 1

    resp = client.get(
        url=f"/api/v1/chat/{chat_id}/message/{message_id}/retrieval_prompt",
    )

    assert resp.status_code == status.HTTP_200_OK


@pytest.mark.anyio
async def test_get_message_retrieval_prompt_not_found(client: TestClient, mocker):
    init_llm_clients(mocker)
    rag_search_ask_question(mocker, use_gpt=True, use_claude3=True)

    chat_id = 1
    message_id = 99999

    resp = client.get(
        url=f"/api/v1/chat/{chat_id}/message/{message_id}/retrieval_prompt",
    )

    assert resp.status_code == status.HTTP_200_OK


@pytest.mark.anyio
async def test_get_summary_no_summary(client: TestClient, mocker):
    init_llm_clients(mocker)
    rag_search_ask_question(mocker, use_gpt=True, use_claude3=True)

    resp = client.get(
        url="/api/v1/chat/2/summarise",
    )

    assert resp.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.anyio
async def test_invalid_query_length_tavily(client: TestClient, mocker):
    init_llm_clients(mocker)
    """ 
    Tavily's schema validation for request objects happens before API key validation so this check can be tested without needing API key
    """
    create_chat_schema = CreateChatSchemaV2(
        options=ChatOptionV2(model=LLMModel.GPT4, search_filters=["DOCUMENT_GENERAL"]),
        description="Explain Issues in china",
    )
    resp = client.post(url="/api/v1/chat", data=create_chat_schema.model_dump_json())

    assert resp.status_code == status.HTTP_201_CREATED

    query = client.put(
        url=f"/api/v1/chat/{resp.json()['id']}",
        data={
            "content": "lol",
        },
    )

    assert query.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.anyio
async def test_create_chat_parent_chat_id_does_not_exist(client: TestClient, mocker):
    init_llm_clients(mocker)
    create_chat_schema = CreateChatSchemaV2(
        options=ChatOptionV2(model=LLMModel.GPT4, search_filters=["DOCUMENT_GENERAL"]),
        parent_chat_id=999999,
        description="Explain Issues in china",
    )
    resp = client.post(url="/api/v1/chat", data=create_chat_schema.model_dump_json())

    assert resp.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.anyio
async def test_ask_llm_question(client: TestClient, mocker):
    init_llm_clients(mocker)
    rag_search_ask_question(mocker, use_gpt=True)

    create_chat_schema = AskLLMQuestionRequestSchema(
        options=ChatOptionV2(model=LLMModel.GPT4, search_filters=["DOCUMENT_GENERAL"]),
        content="Hi llm",
    )
    resp = client.post(
        url="/api/v1/chat/llm",
        data=create_chat_schema.model_dump_json(),
        params={"guardrails": False},
    )

    for data in resp.stream:
        logger.success(data)

    assert resp.status_code == status.HTTP_200_OK


@pytest.mark.anyio
async def test_ask_question_apfs_chat(client: TestClient, mocker):
    settings.APFS_CHAT_MULTI_INDEX_RAG = False
    init_llm_clients(mocker)
    mocker.patch(
        "app.domain.chat_router.workflows.apfs.aggregation.aggregation_os.QueryRewriter.rewrite_query",
        return_value=APFSFilterMetadata(
            search_query="audit opinions using ISA standards",
            b_1=None,
            c_3=None,
            c_1_ii=["ISA"],
            aggregate_fields={"time": "year", "countries": "all"},
            content_date=None,
            countries=None,
            project_numbers=None,
            sectors=None,
        ),
    )
    mocker.patch(
        "app.domain.chat_router.workflows.apfs.aggregation.aggregation_os.OpenSearchClient.search",
        return_value=SearchResponse(
            items=["random lesson"],
            total=4,
            page=1,
            size=4,
            pages=1,
            aggregations=[
                Aggregation(
                    key_as_string="2012-01-01T00:00:00.000Z",
                    key=1325376000000,
                    doc_count=1,
                ),
                Aggregation(
                    key_as_string="2013-01-01T00:00:00.000Z",
                    key=1356998400000,
                    doc_count=12,
                ),
            ],
        ),
    )

    mocker.patch(
        "app.domain.llm_client.service.Claude3SonnetV2Client.send_message",
        return_value=(async_generate_random_string()),
    )

    chat_id = create_apfs_chat(client=client)

    resp = client.put(
        url=f"/api/v1/chat/{chat_id}",
        json={
            "content": "How many audit opinions used ISA standards per year and per country?"
        },
    )

    for data in resp.stream:
        logger.success(data)

    assert resp.status_code == status.HTTP_200_OK


async def test_regenerate_foreign_lang_question(client: TestClient, mocker):
    init_llm_clients(mocker)
    settings.ENABLE_LANGUAGE_DETECTION = True

    mocker.patch(
        "app.domain.llm_chat.chat_utils.ChatUtils.get_async_response",
        return_value=(async_generate_random_string()),
    )

    chat_id = create_new_chat(client)
    resp = client.put(url=f"/api/v1/chat/{chat_id}", json=ask_question_payload())
    assert resp.status_code == status.HTTP_200_OK

    regen = client.post(url=f"/api/v1/chat/{chat_id}/regenerate")

    for data in resp.stream:
        logger.success(data)

    assert regen.status_code == status.HTTP_200_OK


@pytest.mark.anyio
async def test_ask_question_recency_booster(client: TestClient, mocker):
    init_llm_clients(mocker)
    settings.ENABLE_RECENCY_BOOSTING = True
    mocker.patch(
        "app.domain.chat_router.workflows.apfs.aggregation.aggregation_os.QueryRewriter.rewrite_query",
        return_value=GeneralSubqueryMetadata(
            search_query="List number of projects audited using ISA standards, by country",
            domain=Domain.GENERAL,
        ),
    )
    mocker.patch(
        "app.domain.chat_router.workflows.apfs.aggregation.aggregation_os.OpenSearchClient.search",
        return_value=SearchResponse(
            items=["random lesson"], total=4, page=1, size=4, pages=1
        ),
    )

    mocker.patch(
        "app.domain.llm_client.service.GPTClient.send_message",
        return_value=(async_generate_random_string()),
    )

    chat_id = create_new_chat(client=client)

    resp = client.put(
        url=f"/api/v1/chat/{chat_id}",
        json={
            "content": "What are the biggest ADB-funded road projects in the Philippines?"
        },
    )

    for data in resp.stream:
        logger.success(data)

    assert resp.status_code == status.HTTP_200_OK
