export const PRIVATE_PATHS = [/^\/dashboard(\/|$)/, /^\/profile(\/|$)/, /^\/posts\/new$/, /^\/posts\/[^/]+\/edit$/];
export const GUEST_ONLY_PATHS = [/^\/login$/, /^\/register$/];

export const isPrivatePath = (path: string) => PRIVATE_PATHS.some((re) => re.test(path));
export const isGuestOnlyPath = (path: string) => GUEST_ONLY_PATHS.some((re) => re.test(path));
