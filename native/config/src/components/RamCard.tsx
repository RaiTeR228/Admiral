import { Ram } from "@/types/Ram";
import { View, Text } from "react-native";

type Props = {
    product: Ram;
}

const RamCard = ({ product }: Props) => {
    return (
        <View style={{ padding: 10, borderBottomWidth: 1 }}>
            <Text style={{ fontWeight: 'bold' }}>{product.server_info.ram}</Text>
        </View>
    );
}

export default RamCard;