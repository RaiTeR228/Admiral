import { InfoPage } from "@/types/InfoPage";
import { View, Text } from "react-native";

type Props = {
    infoPage: InfoPage;
}

const InfoPageCard = ({ infoPage }: Props) => {
    return (
        <View style={{ padding: 10, borderBottomWidth: 1 }}>
            <Text style={{ fontWeight: 'bold' }}>{infoPage.slug}</Text>
            <Text style={{ fontWeight: 'bold' }}>{infoPage.title}</Text>
            <Text style={{ fontWeight: 'bold' }}>{infoPage.text}</Text>
        </View>
    );
}

export default InfoPageCard;