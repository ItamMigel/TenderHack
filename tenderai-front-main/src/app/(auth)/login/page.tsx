"use client";
import { Form, Input, Checkbox, Button, Divider } from "@heroui/react";
import { Icon } from "@iconify/react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import React from "react";


export default function LoginPage () {
    const [isVisible, setIsVisible] = React.useState(false);

    const toggleVisibility = () => setIsVisible(!isVisible);

    const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        console.log("handleSubmit");
    };

    const router = useRouter();
    return (
        <div className = "flex size-full h-screen w-[384px] items-center justify-center">
            <div className = "flex w-full max-w-sm flex-col gap-4 rounded-large bg-content1 px-8 pb-10 pt-6 shadow-small">
                <div className = "flex flex-col gap-1">
                    <h1 className = "text-large font-medium">Вход в аккаунт</h1>
                </div>

                <Form className = "flex flex-col gap-3" validationBehavior = "native" onSubmit = {handleSubmit}>
                    <Input
                        isRequired
                        label = "Email Адрес"
                        name = "email"
                        placeholder = "Введите ваш Email"
                        type = "email"
                        variant = "bordered"
                    />
                    <Input
                        isRequired
                        endContent = {
                            <button type = "button" onClick = {toggleVisibility}>
                                {isVisible
                                    ? <Icon
                                        className = "pointer-events-none text-2xl text-default-400"
                                        icon = "solar:eye-closed-linear"
                                    />
                                    : <Icon
                                        className = "pointer-events-none text-2xl text-default-400"
                                        icon = "solar:eye-bold"
                                    />
                                }
                            </button>
                        }
                        label = "Пароль"
                        name = "password"
                        placeholder = "Введите пароль"
                        type = {isVisible ? "text" : "password"}
                        variant = "bordered"
                    />
                    <Button className = "w-full" color = "secondary" type = "submit" onPress = {() => { router.push("/"); }}>
                        Войти
                    </Button>
                </Form>

                <p className = "text-center text-small text-text-gray">
                    Нет аккаунта?&nbsp;
                    <Link href = "/register" size = "sm" className = "text-secondary underline">
                        Зарегистрироваться
                    </Link>
                </p>
            </div>
        </div>
    );
}
