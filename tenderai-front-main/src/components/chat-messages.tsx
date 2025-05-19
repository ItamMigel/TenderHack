
import { useMainContext } from "./context";
import { MESSAGE_REVIEW, TChatMessage } from "@/types";
import { cn, ScrollShadow } from "@heroui/react";
import React, { useEffect, useState } from "react";
import DislikeIcon from "@/components/icons/dislike.svg";
import LikeIcon from "@/components/icons/like.svg";
import { useClientApi } from "@/lib/hooks/useClientApi";


export type ChatMessagesProps = {
    messages: TChatMessage[];
    isReviewClickable: boolean;
}
export default function ChatMessages (props: ChatMessagesProps) {
    const { messages, isReviewClickable } = props;


    const { api } = useClientApi();

    const [messagesState, setMessagesState] = useState(messages);

    const {
        sendPrompt, feedbackState,
        setFeedbackState,
        isChatLoading
    } = useMainContext();

    useEffect(() => {
        setMessagesState(messages);
    }, [messages]);

    const onReviewClick = (review: MESSAGE_REVIEW, message: TChatMessage) => {
        if (review === message.review) {
            review = 0;
        }


        api.put(`messages/${message.id}/review`, { review: review }).
            then((res) => {
                const copy: TChatMessage[] = [...messagesState];

                const index = copy.findIndex((mess) => mess.id === message.id);

                copy[index].review = review;
                setMessagesState(copy);
            });
    };

    const sendPrevPrompt = (index: number) => {
        while (index > 0) {
            index -= 1;

            if (messagesState[index].isSelf === true) {
                console.log(messagesState[index]);
                sendPrompt(messagesState[index].text);
                break;
            }
        }
    };
    return <div className = "h-full">
        <ScrollShadow className = "h-full space-y-4 pt-6">

            {messagesState.map((message, index) => {
                return <div key = {message.id}>
                    <div className = "relative flex w-full min-w-0 max-w-full items-start gap-x-3">
                        {!message.isSelf &&
                    <div className = "absolute right-[16px] top-[-16px] h-[32px] w-[64px] rounded-full bg-[#E7EEF7] shadow-xl">
                        <div className = "flex h-[32px] items-center justify-center">
                            <div onClick = {() => { onReviewClick(MESSAGE_REVIEW.like, message); }} className = {cn("flex w-[32px] items-center justify-center", { ["cursor-pointer"]: isReviewClickable })}>
                                <LikeIcon className = {cn("h-[18px]", `${message.review === MESSAGE_REVIEW.like ? "text-success" : "text-text-black"}`)}/>
                            </div>
                            <div onClick = {() => { onReviewClick(MESSAGE_REVIEW.dislike, message); }} className = {cn("flex w-[32px] items-center justify-center", { ["cursor-pointer"]: isReviewClickable })}>
                                <DislikeIcon className = {cn("h-[18px]", `${message.review === MESSAGE_REVIEW.dislike ? "text-danger" : "text-text-black"}`)}/>
                            </div>
                        </div>
                    </div>
                        }
                        <img src = {message.avatarUrl} className = "size-10 rounded-full"/>
                        <div className = {cn({ ["border-1 border-danger"]: message.isSelected }, `flex-1 rounded-xl px-4 py-3 text-[14px] leading-5 whitespace-pre-line ${message.isSelf ? "bg-[#D4DBE6] text-[#3F3F46]" : "bg-[#E7EEF7] text-[#33333E]"}`)}>
                            {message.text}
                        </div>


                    </div>
                    {message.review === MESSAGE_REVIEW.dislike && isReviewClickable &&
                    <div className = "mt-2 pl-12">
                        <div className = "flex h-[58px] w-full items-center justify-between rounded-[12px] px-4 shadow-xl">
                            <div>
                                Для уточнения этого вопроса советуем обратиться к поддержке, либо перегенерировать ответ
                            </div>
                            <div className = "flex items-center gap-x-2">

                                <img className = "cursor-pointer" onClick = {() => { sendPrevPrompt(index); }} src = "/icons/union.png"/>
                                <a href = "tel:89774017505"><img src = "/icons/phone.png"/></a>
                                <img className = "cursor-pointer" onClick = {() => {
                                    setFeedbackState({
                                        isOpen: true,
                                        text: ""
                                    });
                                }} src = "/icons/chat.png"/>
                            </div>

                        </div>
                    </div>
                    }
                </div>;
            })}

            {isChatLoading && <div className = "mt-2 pl-12">
                Думаем   <span className = "inline-flex size-full animate-ping rounded-full bg-sky-400 opacity-75"></span>

            </div>}

        </ScrollShadow>
    </div>;
}
