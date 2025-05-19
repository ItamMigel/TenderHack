import { cookies } from "next/headers";
import axios from "axios";


export async function getCookiesStringSSR () {
    const cookieStore = await cookies();
    const allCookies = cookieStore.getAll();

    let cookiesString = "";
    for (let i = 0; i < allCookies.length; ++i) {
        const cookie = allCookies[i];
        cookiesString += `${cookie.name}=${cookie.value}`;

        if (i < allCookies.length - 1) cookiesString += "; ";
    }
    return cookiesString;
}

export const useServerApi = async () => {
    const cookies = await getCookiesStringSSR();
    const api = axios.create({
        baseURL: `${process.env.BACKEND_URL}`,
        headers: { Cookie: cookies }
    });

    return { api };
};
