"use client";

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";
import { Bell, Check } from "lucide-react";
import { Notification } from "@/types";
import { useMutation, useQuery } from "@tanstack/react-query";
import { getNotifications, markNotificationAsRead } from "@/lib/api/notifications";
import { cn } from "@/lib/utils";
import Link from "next/link";
import { Badge } from "@/components/ui/badge";

export function NotificationCenter() {
  const { data: notifications, refetch } = useQuery<Notification[]>({
    queryKey: ["notifications"],
    queryFn: getNotifications,
  });

  const unreadCount = notifications?.filter((n) => !n.read).length || 0;

  const markAsReadMutation = useMutation({
    mutationFn: markNotificationAsRead,
    onSuccess: () => {
      refetch();
    },
  });

  const handleMarkAsRead = (id: string) => {
    markAsReadMutation.mutate(id);
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon" className="relative">
          <Bell className="h-5 w-5" />
          {unreadCount > 0 && (
            <Badge className="absolute -right-1 -top-1 h-5 w-5 rounded-full p-0 flex items-center justify-center">
              {unreadCount}
            </Badge>
          )}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="w-80" align="end">
        <div className="p-2 font-medium">Notifications</div>
        {notifications?.length ? (
          notifications.map((notification) => (
            <DropdownMenuItem
              key={notification.id}
              className={cn(
                "flex items-start gap-2",
                !notification.read && "bg-muted/50"
              )}
              asChild
            >
              <Link href={notification.link || "#"}>
                <div className="flex-1">
                  <div className="flex justify-between">
                    <p className="font-medium">{notification.title}</p>
                    {!notification.read && (
                      <button
                        onClick={(e) => {
                          e.preventDefault();
                          e.stopPropagation();
                          handleMarkAsRead(notification.id);
                        }}
                        className="text-muted-foreground hover:text-primary"
                      >
                        <Check className="h-4 w-4" />
                      </button>
                    )}
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {notification.message}
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    {new Date(notification.createdAt).toLocaleString()}
                  </p>
                </div>
              </Link>
            </DropdownMenuItem>
          ))
        ) : (
          <div className="p-4 text-center text-muted-foreground text-sm">
            No notifications
          </div>
        )}
        <div className="p-2 text-center">
          <Button variant="ghost" size="sm" asChild>
            <Link href="/notifications">View all</Link>
          </Button>
        </div>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}