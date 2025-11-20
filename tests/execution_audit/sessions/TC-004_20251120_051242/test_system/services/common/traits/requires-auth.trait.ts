export interface User {
  id: string;
  email: string;
  roles: string[];
}

export interface RequiresAuth {
  validateToken(token: string): Promise<boolean>;
  getCurrentUser(token: string): Promise<User>;
  checkPermission(user: User, permission: string): boolean;
}
