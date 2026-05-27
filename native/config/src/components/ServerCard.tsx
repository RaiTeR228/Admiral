import { Server } from "@/types/Server";
import { View, Text } from "react-native";

type Props = {
    product: Server;
}

const ProductCard = ({ product }: Props) => {
    return (
        <View style={{ padding: 10, borderBottomWidth: 1 }}>
            <Text style={{ fontWeight: 'bold' }}>{product.cpu_name}</Text>
            <Text>Ядра: {product.cores}</Text>
            <Text>Потоки: {product.threads}</Text>
        </View>
    );
}

export default ProductCard;