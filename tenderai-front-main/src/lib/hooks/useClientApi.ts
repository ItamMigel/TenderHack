import { useMemo } from "react";
import axios from "axios";


export const useClientApi = (config = {}) => {
    const api = useMemo(() => {
        const instance = axios.create({ baseURL: `${process.env.NEXT_PUBLIC_BACKEND_URL}`, });

        instance.defaults.headers.post["Access-Control-Allow-Origin"] = "*";

        return instance;
    }, []);

    return { api };
};
