import { StyleSheet, FlatList } from 'react-native';

import { Text, View } from '@/components/Themed';
// import { useSampleGetSample } from '@/api/client';

export default function TabOneScreen() {
  // const { data, isLoading, error } = useSampleGetSample();

  // if (isLoading) {
  //   return <Text>Loading...</Text>;
  // }

  // if (error) {
  //   return <Text>Error fetching data</Text>;
  // }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Sample API Data</Text>
      <FlatList
        data={data || []}
        keyExtractor={(item) => item.draw_number.toString()}
        renderItem={({ item }) => (
          <View style={styles.itemContainer}>
            {/* <Text>Draw #{item.draw_number}</Text> */}
            <Text>{item.numbers}</Text>
          </View>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingTop: 40,
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 20,
  },
  itemContainer: {
    padding: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#ccc',
  },
});
