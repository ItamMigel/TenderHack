"use client";
import ChatMessages from "@/components/chat-messages";
import { assistantsMock, chatMessagesMock, questionsMock } from "@/mocks";
import { MESSAGE_REVIEW, TChatMessage, TQuestion } from "@/types";
import { Table, TableHeader, TableColumn, TableBody, TableRow, TableCell, Pagination, Divider, Modal, ModalBody, ModalContent, ModalHeader, Button, cn } from "@heroui/react";
import React, { useCallback, useEffect, useState } from "react";
import DislikeIcon from "@/components/icons/dislike.svg";
import LikeIcon from "@/components/icons/like.svg";
import { useClientApi } from "@/lib/hooks/useClientApi";


const tableColumns = [
    {
        name: "ID вопроса",
        uid: "id"
    },
    {
        name: "Ассистент",
        uid: "assistant"
    },
    {
        name: "База знаний",
        uid: "bd"
    },
    {
        name: "Кластер",
        uid: "cluster"
    },
    {
        name: "Вопрос",
        uid: "question"
    },
    {
        name: "Оценка",
        uid: "review"
    },
    {
        name: "Дата",
        uid: "date"
    },
    {
        name: "Действия",
        uid: "actions"
    },
];
export default function QuestionsPage () {
    const [dialogueModalState, setDialogueModalState] = useState<{isModal: boolean, dialogueHistory:TChatMessage[]}>({
        isModal: false,
        dialogueHistory: []
    });


    const renderQuestionCell = useCallback((question: TQuestion, columnKey: string) => {
        switch (columnKey) {
        case "id":
            return <div className = "text-center">
                {question.id}
            </div>;
        case "assistant":
            return <div className = "flex w-full justify-center gap-x-1.5">
                <img className = "size-10" src = {question.assistant.avatarUrl}/>
                <div>
                    <div className = "text-[14px] leading-[20px]">
                        {question.assistant.title}
                    </div>
                    <div className = "text-[12px] leading-[16px]">
                        {question.assistant.neuralNetworkTitle}
                    </div>
                </div>

            </div>;
        case "bd":
            return <div className = "text-center">
                {question.assistant.dataset.title}
            </div>;
        case "cluster":
            return <div>
                <div className = "flex h-[28px] w-fit items-center gap-x-1.5 rounded-[8px] bg-primary-dark py-1 pl-2 pr-3">
                    <div className = "size-[7px] rounded-full" style = {{ backgroundColor: question.cluster.color }}/>
                    <div className = "text-[14px] leading-[20px]">{question.cluster.title}</div>
                </div>
            </div>;
        case "question":
        {
            const selectedMessage = question.dialogue.find((message) => { return message.isSelected; });
            if (!selectedMessage) {
                return <div>Не найдено</div>;
            }
            return <div>{selectedMessage.text.substring(0, Math.min(24, selectedMessage.text.length))}</div>;
        }
        case "review":
        { const selectedMessage = question.dialogue.find((message) => { return message.isSelected; });
            if (!selectedMessage) {
                return <div>Не найдено</div>;
            }
            return <div className = "mx-auto w-fit">{question.review === MESSAGE_REVIEW.like &&
                <LikeIcon className = {cn("h-[18px]", `${question.review === MESSAGE_REVIEW.like ? "text-success" : "text-text-black"}`)}/>
            }
            {question.review === MESSAGE_REVIEW.dislike &&
                <DislikeIcon className = {cn("h-[18px]", `${question.review === MESSAGE_REVIEW.dislike ? "text-danger" : "text-text-black"}`)}/>
            }
            </div>;
        }
        case "date":
        {
            const dateText = new Date(question.askedAt).toLocaleDateString("ru");
            return <div>{dateText}</div>;
        }
        case "actions":
            return <div>
                <Button onPress = {() => {
                    setDialogueModalState({
                        isModal: true,
                        dialogueHistory: question.dialogue
                    });
                }}>
                    Смотреть
                </Button>
            </div>;
        }
        return <div>

        </div>;
    }, []);

    const [questionsState, setQuestionsState] = useState({
        totalCount: questionsMock.length,
        createdAtOffset: Date.now(),
        questions: questionsMock,
        review: 0,
        currentPage: 1,
        limit: 10,
    });


    const { api } = useClientApi();

    const getPage = (page: number) => {
        api.get(`/general/history?limit=10&offset=${10 * (page - 1)}`).then((res) => {
            const questionsNew = [];
            let i = 0;
            for (const question of res.data.items) {
                const dialogue = [];
                let review = 0;
                for (const message of question.messages) {
                    if (message.review !== 0) {
                        review = message.review;
                    }
                    dialogue.push({
                        id: message.id,
                        avatarUrl: message["is_self"] ? "/uploads/users/user.png" : "/uploads/assistants/1.png",
                        text: message.text,
                        isSelf: message["is_self"],
                        isSelected: message.text === question.question ? true : false,
                        review: message.review
                    });
                }
                const base = {
                    id: i,
                    assistant: assistantsMock[0],
                    dialogue: dialogue,
                    askedAt: question.date * 1000,
                    review: review,
                    cluster: {
                        id: "1",
                        color: "#17C964",
                        title: question.cluster
                    }
                };
                i += 1;
                questionsNew.push(base);
            }
            setQuestionsState((state) => {
                state.questions = questionsNew;
                state.totalCount = res.data.total;
                return { ...state };
            });
        });
    };
    useEffect(() => {
        getPage(1);
    }, []);


    return (
        <div className = "flex h-full flex-col overflow-y-auto pb-2 pt-12">
            <Modal
                size = "sm"
                className = "min-h-[459px]"
                isOpen = {dialogueModalState.isModal}
                onOpenChange = {(isOpen) => {
                    if (!isOpen) {
                        setDialogueModalState({
                            isModal: false,
                            dialogueHistory: []
                        });
                    }
                }}
                scrollBehavior = "outside"
            >
                <ModalContent>
                    {(onClose) => <>
                        <ModalHeader>
                            <div className = "w-full pt-5">
                                <div className = "text-[18px] font-medium leading-[28px]">
                                    Запись диалога
                                </div>

                            </div>
                        </ModalHeader>
                        <ModalBody>
                            <div className = "space-y-2 pb-4">
                                <Divider orientation = "horizontal" className = "mb-3"/>
                                {dialogueModalState.dialogueHistory.length > 0 &&
                                    <ChatMessages messages = {dialogueModalState.dialogueHistory} isReviewClickable = {false}/>
                                }


                            </div>
                        </ModalBody>
                    </>}
                </ModalContent>

            </Modal>
            <div>
                <div>
                    <div className = "text-[30px] font-bold leading-[36px]">Вопросы и кластеры</div>
                    <div className = "mb-6 text-[16px] leading-[24px] text-text-gray">Ознакомьтесь с вопросами</div>
                </div>
                <Table
                    isStriped
                    aria-label = "Example table with custom cells"
                    align = "center"
                    classNames = {{ tr: "" }}
                >
                    <TableHeader columns = {tableColumns} className = "bg-primary">
                        {(column) => <TableColumn key = {column.uid}>
                            {column.name}
                        </TableColumn>
                        }
                    </TableHeader>
                    <TableBody items = {questionsState.questions}>
                        {(item) => <TableRow key = {item.id}>
                            {(columnKey) => <TableCell>{renderQuestionCell(item, columnKey)}</TableCell>}
                        </TableRow>
                        }
                    </TableBody>
                </Table>
            </div>
            <div className = "min-h-0 flex-1 pb-8">
                <div className = "flex size-full flex-col items-center justify-end">
                    <Pagination
                        onChange = {getPage}
                        classNames = {{
                            wrapper: "bg-primary",
                            prev: "bg-primary",
                            next: "bg-primary"
                        }} isCompact showControls color = "secondary" total = {Math.ceil(questionsState.totalCount / questionsState.limit)} page = {questionsState.currentPage}/>
                </div>
            </div>
        </div>

    );
}
