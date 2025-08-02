import { useRealms } from "@/api/realms";
import { RealmCard } from "@/components/RealmCard/RealmCard";
import { navigationStore } from "@/stores/NavigationStore";

export function RealmsPage() {
    const { data: realms } = useRealms();

    return (
        <div className="grid grid-cols-2 gap-4 p-2">
            {realms.map((realm) => (
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