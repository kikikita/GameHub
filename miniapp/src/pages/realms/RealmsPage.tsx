import { useRealms } from "@/api/realms";
import { RealmCard } from "@/components/RealmCard/RealmCard";
import { navigationStore } from "@/stores/NavigationStore";

import { CreateNewStoryCard } from "@/components/CreateNewStoryCard/CreateNewStoryCard";
import { useMemo } from "react";

export function RealmsPage() {
    const { data: realms } = useRealms();

    const cards = useMemo(() =>     [
        ...realms.slice(0, 2).map((realm) => (
            <RealmCard
                key={realm.id}
                {...realm}
                className="aspect-[3/4]"
                onClick={() => navigationStore.selectRealm(realm.id)}
            />
        )),
        <CreateNewStoryCard key="create-new-story"  className="aspect-[3/4]" />,
        ...realms.slice(2).map((realm) => (
            <RealmCard
                key={realm.id}
                {...realm}
                className="aspect-[3/4]"
                onClick={() => navigationStore.selectRealm(realm.id)}
            />
        )),
    ], [realms]);

    return (
        <div className="grid grid-cols-2 gap-4 p-2">
            {cards}
        </div>
    );
}