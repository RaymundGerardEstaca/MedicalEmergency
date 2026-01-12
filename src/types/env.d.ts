declare global {
    namespace NodeJS {
        interface ProcessEnv {
            EXPO_PUBLIC_GOOGLE_WEB_CLIENT_ID: string | undefined;
            [key: string]: string | undefined;
        }
    }
    var process: {
        env: NodeJS.ProcessEnv;
    };
}

// Ensure this file is treated as a module
export { };

