import { Disk } from "@/types/Disk";
import { View, Text } from "react-native";

type Props = {
    product: Disk;
}

const DiskCard = ({ product }: Props) => {
    return (
        <View style={{ padding: 10, borderBottomWidth: 1 }}>
            <Text style={{ fontWeight: 'bold' }}>{product.disk.disk_name}</Text>
        </View>
    );
}

export default DiskCard;