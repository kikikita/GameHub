import { getRealms as getRealmsApi } from "@/api/realms";
import { RealmCard } from "@/components/RealmCard/RealmCard";
import { use } from "react";
import { navigationStore } from "@/stores/NavigationStore";

const getRealms = getRealmsApi();
export function RealmsPage() {
    const realms = use(getRealms);

    return (
        <div className="grid grid-cols-2 gap-4 p-2">
            {realms.realms.map((realm) => (
                <RealmCard
                    key={realm.id}
                    {...realm}
                    className="aspect-[3/4]"
                    onClick={() => navigationStore.selectRealm(realm.id)}
                />
            ))}
        </div>
    );
}