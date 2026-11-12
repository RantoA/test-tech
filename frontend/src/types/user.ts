export interface User {
  id: string;
  name: string;
  email: string;
  created_at: string;
  updated_at: string;
}

export interface Author {
  id: string;
  name: string;
}

export interface AuthPayload {
  user: User;
  access_token: string;
  token_type: string;
  expires_in: number;
}
