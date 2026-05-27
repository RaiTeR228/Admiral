import {TemperatureData} from "@/types/Temperature";
import { View, Text } from "react-native";

type Props = {
    product: TemperatureData;
}

const TemperatureCard = ({ product }: Props) => {
    return (
        <View style={{ padding: 10, borderBottomWidth: 1 }}>
            <Text style={{ fontWeight: 'bold' }}>{product.temperature.current_temp}°C</Text>
        </View>
    );
}

export default TemperatureCard;