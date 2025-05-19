import { TChatMessage, MESSAGE_REVIEW, TAssistant, TQuestion, TPromptIdea, TPromptIdeaCard, TQuestionCluster, TStatsChip } from "@/types";


export const promptIdeasMock: TPromptIdea[] = [
    {
        title: "Как создать новый товар",
        description: "дай инструкцию",
        prompt: ""
    },
    {
        title: "10 идей для привлечения клиентов",
        description: "расскажи как работает реклама",
        prompt: ""
    },
    {
        title: "Что такое Мендекс Маркет",
        description: "дай объяснение что это",
        prompt: ""
    },
    {
        title: "Что такое Мендекс Маркет",
        description: "дай объяснение что это",
        prompt: ""
    },
];

export const chatMessagesMock: TChatMessage[] = [
    {
        id: "1",
        avatarUrl: "/uploads/users/user.png",
        text: "Расскажи о 5 вариантах, с помощью которых я могу на сайте разместить свое объявление так, чтобы его увидело много людей!",
        isSelf: true,
        isSelected: false,
        review: MESSAGE_REVIEW.none
    },
    {
        id: "2",
        avatarUrl: "/uploads/assistants/1.png",
        text: "Конечно! На Мендекс Маркете мжно размещать товары так:\nКарточка товара: Все увидят ваш товар в списке;\nЕще что-то: Раздел для искушенных покупателей\nБаннер с рекламой: За дополнительную плату\nЕще один вариант: Я устал придумывать, тут просто текст\nИ самый крайний: Для красивого макета",
        isSelf: false,
        isSelected: true,
        review: MESSAGE_REVIEW.dislike
    },
    {
        id: "4",
        avatarUrl: "/uploads/users/user.png",
        text: "Cпасибо, очень круто!",
        isSelf: true,
        isSelected: false,
        review: MESSAGE_REVIEW.none
    },
];

export const assistantsMock: TAssistant[] = [
    {
        id: "1",
        gradient: "0.35turn, #3f87a6, #ebf8e1, #f69d3c",
        avatarUrl: "/uploads/assistants/1.png",
        neuralNetworkTitle: "ChatGPT 4",
        title: "Ассистент 1",
        settings: {
            temperature: 0.1,
            maxLength: 1024,
            topP: 0.5,
            frequencyPenalty: 1.3,
            presencePenalty: 1.2
        },
        dataset: {
            id: "1",
            title: "MandexMarketV1",

        }
    },
    {
        id: "2",
        gradient: "0.35turn, #3f87a6, #ebf8e1, #f69d3c",
        avatarUrl: "/uploads/assistants/2.png",
        neuralNetworkTitle: "ChatGPT 4",
        title: "Ассистент 2",
        settings: {
            temperature: 0.1,
            maxLength: 1024,
            topP: 0.5,
            frequencyPenalty: 1.3,
            presencePenalty: 1.2
        },
        dataset: {
            id: "2",
            title: "MandexMarketV1",

        }
    },
    {
        id: "3",
        gradient: "0.35turn, #3f87a6, #ebf8e1, #f69d3c",
        avatarUrl: "/uploads/assistants/3.png",
        neuralNetworkTitle: "ChatGPT 4",
        title: "Ассистент 3",
        settings: {
            temperature: 0.1,
            maxLength: 1024,
            topP: 0.5,
            frequencyPenalty: 1.3,
            presencePenalty: 1.2
        },
        dataset: {
            id: "3",
            title: "MandexMarketV1",

        }
    },
    {
        id: "4",
        gradient: "0.25turn, #3f87a6, #ebf8e1, #f69d3c",
        avatarUrl: "/uploads/assistants/4.png",
        neuralNetworkTitle: "ChatGPT 4",
        title: "Ассистент 4",
        settings: {
            temperature: 0.1,
            maxLength: 1024,
            topP: 0.5,
            frequencyPenalty: 1.3,
            presencePenalty: 1.2
        },
        dataset: {
            id: "4",
            title: "MandexMarketV1",

        }
    },
    {
        id: "5",
        gradient: "0.25turn, #3f87a6, #ebf8e1, #f69d3c",
        avatarUrl: "/uploads/assistants/5.png",
        neuralNetworkTitle: "ChatGPT 4",
        title: "Ассистент 5",
        settings: {
            temperature: 0.1,
            maxLength: 1024,
            topP: 0.5,
            frequencyPenalty: 1.3,
            presencePenalty: 1.2
        },
        dataset: {
            id: "5",
            title: "MandexMarketV1",
        }
    }
];


export const questionsMock: TQuestion[] = [
    {
        id: "1",
        assistant: assistantsMock[0],
        dialogue: chatMessagesMock,
        askedAt: 1743820854471,
        cluster: {
            id: "1",
            color: "#17C964",
            title: "Безопасность"
        }
    },
    {
        id: "2",
        assistant: assistantsMock[1],
        dialogue: chatMessagesMock,
        askedAt: 1743820854471,
        cluster: {
            id: "2",
            color: "#FFCC00",
            title: "Авторизация"
        }
    },
    {
        id: "3",
        assistant: assistantsMock[2],
        dialogue: chatMessagesMock,
        askedAt: 1743820854471,
        cluster: {
            id: "3",
            color: "#007AFF",
            title: "Закупки"
        }
    },
    {
        id: "4",
        assistant: assistantsMock[1],
        dialogue: chatMessagesMock,
        askedAt: 0,
        cluster: {
            id: "2",
            color: "#FFCC00",
            title: "Авторизация"
        }
    },
];

export const promptIdeasCardsMock: TPromptIdeaCard[] = [
    {
        id: "1",
        title: "Популярные вопросы",
        iconUrl: "solar:mask-happly-linear",
        ideas: [
            {
                title: "Где изменить описание магазина?",
                description: "",
                prompt: ""
            },
            {
                title: "Что умеет ваш новый крутой RAG бот?",
                description: "",
                prompt: ""
            },
        ],
    },
    {
        id: "2",
        title: "Работа с платформой",
        iconUrl: "solar:magic-stick-3-linear",
        ideas: [
            {
                title: "Как написать описание товара с помощью ИИ?",
                description: "",
                prompt: ""
            },
            {
                title: "Как добавить цветной значок на свой магазин?",
                description: "",
                prompt: ""
            },
        ],
    },
    {
        id: "3",
        title: "Важное",
        iconUrl: "solar:shield-warning-outline",
        ideas: [
            {
                title: "Как изменились правила оформления карточек?",
                description: "",
                prompt: ""
            },
            {
                title: "Как изменились правила оформления карточек?",
                description: "",
                prompt: ""
            },
            {
                title: "Еще какой-нибудь крутой вопрос",
                description: "",
                prompt: ""
            },
        ],
    },
];


export const clustersMock: TQuestionCluster[] = [
    {
        id: "1",
        color: "#17C964",
        title: "Безопасность"
    },
    {
        id: "2",
        color: "#FFCC00",
        title: "Авторизация"
    },
    {
        id: "3",
        color: "#007AFF",
        title: "Закупки"
    }
];


export const chartMock = {
    series: [
        {
            name: "Безопасность",
            color: "#17C964",
            data: [30, 40, 35, 50, 49, 60, 70, 91, 125]
        },
        {
            name: "Авторизация",
            color: "#FFCC00",
            data: [40, 50, 25, 10, 69, 40, 70, 41, 115]
        }
    ],
    xaxis: { type: "category" }
};


export const statsChipsMock: TStatsChip[] = [
    {
        title: "Запросов за сегодня",
        value: "147",
        change: "0.2%",
        changeType: "neutral",
        iconUrl: "solar:users-group-rounded-linear",
    },
    {
        title: "Лайков за сегодня",
        value: "5235",
        change: "52.3%",
        changeType: "positive",
        iconUrl: "solar:wallet-money-outline",
    },
    {
        title: "Лайков за сегодня",
        value: "4029",
        change: "-13.2%",
        changeType: "negative",
        iconUrl: "solar:wallet-money-outline",
    },
];
