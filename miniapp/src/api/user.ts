import { useMutation, useQueryClient, useSuspenseQuery } from "@tanstack/react-query";
import { API_URL } from "./common";
import { getInitData } from "@/telegram/init";

export interface UserDTO {
  language: string | null;
  image_format: string | null;
  wishes: number;
  energy: number;
}

interface User {
    language: string;
    image_format: "vertical" | "horizontal";
    wishes: number;
    energy: number;
}

export function getUser(): Promise<User> {
  return fetch(`${API_URL}/api/v1/users/me/`, {
    headers: {
      "Content-Type": "application/json",
      'Authorization': `tma ${getInitData()}`,
    },
  }).then((res) =>
    {
        if (!res.ok) {
            return {
                language: "en",
                image_format: "vertical",
                wishes: 0,
                energy: 0,
            }
        }
        return res.json();
    }
  ).then<User>((data) => ({
    language: data.language ?? "en",
    image_format: data.image_format ?? "vertical",
    wishes: data.wishes ?? 0,
    energy: data.energy ?? 0,
  }));
}

export function useUser() {
  return useSuspenseQuery({
    queryKey: ["user"],
    queryFn: getUser,
  });
}

interface UserUpdate {
  language?: string;
  image_format?: "vertical" | "horizontal";
}

export function updateUser(user: UserUpdate): Promise<User> {
  return fetch(`${API_URL}/api/v1/users/me/`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      'Authorization': `tma ${getInitData()}`,
    },
    body: JSON.stringify(user),
  }).then((res) => res.json());
}

export function useUpdateUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: updateUser,
    // Optimistic update
    onMutate: async (newUser: UserUpdate) => {
      await queryClient.cancelQueries({ queryKey: ["user"] });

      const previousUser = queryClient.getQueryData<User>(["user"]);

      // Optimistically update the user data
      queryClient.setQueryData<User>(["user"], (old) => {
        if (!old) return { ...newUser, wishes: 0, energy: 0, language: "en", image_format: "vertical" };
        return {
          ...old,
          ...newUser,
        };
      });

      return { previousUser };
    },
    onError: (_err, _newUser, context) => {
      // Rollback to previous user data if mutation fails
      if (context?.previousUser) {
        queryClient.setQueryData(["user"], context.previousUser);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["user"] });
    },
  });
}